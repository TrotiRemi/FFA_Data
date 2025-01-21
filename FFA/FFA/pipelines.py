import re
import scrapy
from pymongo import MongoClient
from datetime import datetime

class DataCleaningPipeline:
    def round_to_two_decimals(self, value):
        """
        Arrondit une valeur à deux décimales si c'est un float.
        Retourne la valeur brute si ce n'est pas un float.
        """
        if isinstance(value, float):
            return round(value, 2)
        return value

    def __init__(self, mongo_uri, mongo_db, collection_name):
        """
        Initialisation du pipeline avec les paramètres MongoDB.
        """
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.collection_name = collection_name
        self.existing_records = set()

    @classmethod
    def from_crawler(cls, crawler):
        """
        Initialise le pipeline en utilisant les paramètres de Scrapy.
        """
        return cls(
            mongo_uri=crawler.settings.get("MONGO_URI", "mongodb://localhost:27017/"),
            mongo_db=crawler.settings.get("MONGO_DATABASE", "athle_database"),
            collection_name=crawler.settings.get("MONGO_COLLECTION", "results")
        )

    def open_spider(self, spider):
        """
        Connexion à MongoDB et chargement des enregistrements existants.
        """
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.collection = self.db[self.collection_name]

        # Charger les enregistrements existants pour éviter les doublons
        self.existing_records = {
            (doc.get("rank"), doc.get("time"), doc.get("athlete"),
             doc.get("competition_date"), doc.get("competition_name"))
            for doc in self.collection.find({}, {"rank": 1, "time": 1, "athlete": 1, "competition_date": 1, "competition_name": 1})
        }

    def close_spider(self, spider):
        """
        Fermeture de la connexion à MongoDB.
        """
        self.client.close()

    def is_time_format(self, time_str):
        """
        Détermine si le champ `time` est un format de temps ou de distance.
        """
        time_pattern = re.match(r"^\d+h\d+'\d+''$|^\d+'\d+''$|^\d+h\d+'$|^\d+''$", time_str)
        return bool(time_pattern)
    
    def process_item(self, item, spider):
        """
        Processus pour traiter chaque élément en fonction des cas prioritaires,
        tout en évitant les doublons basés sur des colonnes clés.
        """
        # Vérification des doublons
        record_key = (
            item.get("rank"),
            item.get("time"),
            item.get("athlete"),
            item.get("competition_date"),
            item.get("competition_name"),
        )
        if record_key in self.existing_records:
            raise scrapy.exceptions.DropItem(f"Doublon détecté et supprimé : {item}")

        # Ajouter le record aux enregistrements existants
        self.existing_records.add(record_key)

        # Vérification si le champ `athlete` est valide
        if not item.get('athlete') or item['athlete'].strip() == "Inconnu":
            raise scrapy.exceptions.DropItem(f"Ligne ignorée car `athlete` est vide : {item}")
        
        # Conversion de `rank` en chaîne de caractères
        if "rank" in item:
            item["rank"] = str(item["rank"]) if item["rank"] is not None else None

        # Formatage de la date pour ElasticSearch
        if "competition_date" in item:
            try:
                item["competition_date"] = self.format_date_for_es(item["competition_date"])
            except ValueError:
                raise scrapy.exceptions.DropItem(f"Date invalide trouvée : {item['competition_date']}")

        # Extraction et calcul des autres champs
        item['distance'] = self.extract_distance(item.get('full_line'))
        if item['distance'] > 0:  # Cas où la distance est présente dans `full_line`
            item['Minute_Time'] = self.convert_to_minutes(item.get('time'))
        else:
            is_time_format = self.is_time_format(item.get('time'))
            if not is_time_format:  # `time` est une distance
                item['distance'] = self.extract_distance_from_time(item['time'])
                item['Minute_Time'] = self.extract_duration_from_full_line(item.get('full_line'))
            else:
                item['Minute_Time'] = self.convert_to_minutes(item['time'])
                item['distance'] = 0  # Distance inconnue si non trouvée

        if item.get('distance') and item['Minute_Time']:
            try:
                item['vitesse'] = (item['distance'] / 1000) / (item['Minute_Time'] / 60)
            except (ValueError, TypeError):
                item['vitesse'] = 0
        else:
            item['vitesse'] = 0

        for field in ['distance', 'Minute_Time', 'vitesse']:
            if field in item:
                item[field] = self.round_to_two_decimals(item[field])

        if 'club' in item and (not item['club'] or item['club'].strip() == ""):
            item['club'] = "No Club"

        # Insérer dans MongoDB
        self.collection.insert_one(dict(item))

        return item

    def format_date_for_es(self, date_str):
        """
        Convertit une date en chaîne au format ElasticSearch 'yyyy-MM-dd'.
        """
        try:
            # Vérifiez si la date est déjà au format attendu
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str  # Retournez la date telle quelle si elle est correcte
        except ValueError:
            # Essayez de la convertir depuis d'autres formats possibles
            try:
                return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")  # Exemple : "01/03/2020" -> "2020-03-01"
            except ValueError:
                raise ValueError(f"Format de date non reconnu pour {date_str}")

    def extract_distance(self, full_line):
        if not full_line:
            return 0

        # Recherche des cas prioritaires
        if re.search(r"1/2\s?marathon|semi[-\s]?marathon", full_line, re.IGNORECASE):
            return 21097.5
        if re.search(r"marathon", full_line, re.IGNORECASE):
            return 42195

        # Recherche des distances en mètres
        match_meters = re.findall(r"(\d+)\s?[mM]", full_line)
        if match_meters:
            return max(float(m) for m in match_meters)

        # Recherche des distances en kilomètres
        match_kilometers = re.search(r"(\d+)\s?[kK][mM]", full_line)
        if match_kilometers:
            return float(match_kilometers.group(1)) * 1000

        return 0

    def extract_distance_from_time(self, time_str):
        """
        Extrait la distance depuis le champ `time` si c'est une distance (e.g., "190km500m").
        """
        match_distance = re.match(r"(?:(\d+)\s?[kK][mM])?\s?(?:(\d+)\s?[mM])?", time_str)
        if match_distance:
            kilometers = match_distance.group(1)
            meters = match_distance.group(2)
            distance_in_meters = 0
            if kilometers:
                distance_in_meters += int(kilometers) * 1000
            if meters:
                distance_in_meters += int(meters)
            return distance_in_meters
        return 0

    def extract_duration_from_full_line(self, full_line):
        """
        Extrait la durée en minutes depuis `full_line` si c'est une course chronométrée (e.g., "34 heures").
        """
        match_hours = re.search(r"(\d+)\s?(?:heures|heure|h)", full_line, re.IGNORECASE)
        if match_hours:
            hours = int(match_hours.group(1))
            return hours * 60
        return 0

    def convert_to_minutes(self, time_str, distance=None):
        """
        Convertit un format de temps (exemple : 1h15'19'') en minutes.
        """
        if not time_str:
            return None

        # Vérifier la présence d'informations entre parenthèses
        match_parentheses = re.search(r"\((.*?)\)", time_str)
        if match_parentheses:
            time_str = match_parentheses.group(1)
        else:
            time_str = re.sub(r"[^\d'hm'':]+$", "", time_str).strip()

        # Correspondances des formats de temps
        match_hms_colon = re.match(r"^(\d+):(\d+):(\d+)$", time_str)
        match_ms_double_apostrophe = re.match(r"^(\d+)'(\d+)''$", time_str)
        match_seconds_only = re.match(r"^(\d+)''$", time_str)
        match_hms = re.match(r"(?:(\d+)h)?(?:(\d+)'|(\d+):)?(\d+)?", time_str)

        # Extraction selon le format détecté
        if match_hms_colon:
            hours = int(match_hms_colon.group(1))
            minutes = int(match_hms_colon.group(2))
            seconds = int(match_hms_colon.group(3))
        elif match_ms_double_apostrophe:
            hours = 0
            minutes = int(match_ms_double_apostrophe.group(1))
            seconds = int(match_ms_double_apostrophe.group(2))
        elif match_seconds_only:
            seconds = int(match_seconds_only.group(1))
            if distance and distance > 1000:
                return seconds
            return seconds / 60
        elif match_hms:
            hours = int(match_hms.group(1)) if match_hms.group(1) else 0
            minutes = int(match_hms.group(2) or match_hms.group(3)) if (match_hms.group(2) or match_hms.group(3)) else 0
            seconds = int(match_hms.group(4)) if match_hms.group(4) else 0
        else:
            return None

        return hours * 60 + minutes + seconds / 60

