import re
import scrapy
from pymongo import MongoClient

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
        # Initialisation des mappings
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.collection_name = collection_name
        self.level_mapping = {
            'Rég': 'Régional',
            'Nat': 'National',
            'Int': 'Interrégional',
            'Dép': 'Départemental'
        }
        self.ligue_mapping = {
            "NORM": "Normandie",
            "BFC": "Bourgogne-Franche-Comté",
            "OCC": "Occitanie",
            "N-A": "Nouvelle-Aquitaine",
            "PAC": "Provence-Alpes-Côte d'Azur",
            "CEN": "Centre-Val de Loire",
            "P-L": "Pays de la Loire",
            "H-F": "Hauts-de-France",
            "IDF": "Île-de-France",
            "ARA": "Auvergne-Rhône-Alpes",
            "BRE": "Bretagne",
            "GE": "Grand Est",
            "NAQ": "Nouvelle-Aquitaine",
            "COR": "Corse",
            "GUY": "Guyane",
            "GUA": "Guadeloupe",
            "MAR": "Martinique",
            "REU": "La Réunion",
            "MAY": "Mayotte"
        }
    @classmethod
    def from_crawler(cls, crawler):
        """
        Initialisation avec les paramètres depuis les settings.
        """
        return cls(
            mongo_uri=crawler.settings.get("MONGO_URI", "mongodb://localhost:27017/"),
            mongo_db=crawler.settings.get("MONGO_DATABASE", "athle_database"),
            collection_name=crawler.settings.get("MONGO_COLLECTION", "results"),
        )

    def open_spider(self, spider):
        """
        Connexion à MongoDB.
        """
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.collection = self.db[self.collection_name]

    def close_spider(self, spider):
        """
        Fermeture de la connexion à MongoDB.
        """
        self.client.close()
    def process_item(self, item, spider):
        # Nettoyage et transformation des champs
        if not item.get('athlete') or item['athlete'].strip() == "Inconnu":
            raise scrapy.exceptions.DropItem(f"Ligne ignorée car `athlete` est vide : {item}")
        
        # Extraire la distance
        if 'full_line' in item:
            item['distance'] = self.extract_distance(item['full_line'])

        # Extraire le sexe
        if 'full_line' in item:
            item['sex'] = self.extract_sex(item['full_line'])

        # Conversion du temps en minutes
        if 'time' in item and item['time']:
            item['Minute_Time'] = self.convert_to_minutes(item.get('time'))
        else:
            item['Minute_Time'] = 0

        # Calcul de la vitesse (si distance existe)
        if item.get('distance') and item['Minute_Time']:
            try:
                item['vitesse'] = (item['distance'] / 1000) / (item['Minute_Time'] / 60)
            except (ValueError, TypeError):
                item['vitesse'] = 0
        else:
            item['vitesse'] = 0

        # Arrondir les champs numériques
        for field in ['distance', 'Minute_Time', 'vitesse']:
            if field in item:
                item[field] = self.round_to_two_decimals(item[field])

        # Nettoyage du niveau
        if 'level' in item:
            item['level'] = self.level_mapping.get(item['level'], item['level'])
        
        # Nettoyage du club
        if 'club' in item:
            if not item['club'] or item['club'].strip() == "":
                item['club'] = "No Club"

        # Remplacement des abréviations de ligue
        if 'ligue' in item:
            item['ligue_complet'] = self.ligue_mapping.get(item['ligue'], item['ligue'])

        return item

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

    def extract_sex(self, full_line):
        """
        Extrait le sexe (M ou F) à partir de la ligne complète.
        """
        match_sex = re.search(r"Chr\s?:\s?([MF])", full_line, re.IGNORECASE)
        if match_sex:
            return match_sex.group(1).upper()
        return "Unknown"

    def convert_to_minutes(self, time_str):
        """
        Convertit un format de temps (exemple : 1h15'19'') en minutes.
        """
        if not time_str:
            return None

        match_hms_colon = re.match(r"^(\d+):(\d+):(\d+)$", time_str)
        match_ms_double_apostrophe = re.match(r"^(\d+)'(\d+)''$", time_str)
        match_negative_ms = re.match(r"^- \((\d+)'(\d+)''\)$", time_str)
        match_seconds_only = re.match(r"^(\d+)''$", time_str)
        match_hms = re.match(r"(?:(\d+)h)?(?:(\d+)'|(\d+):)?(\d+)?", time_str)

        if match_hms_colon:
            hours = int(match_hms_colon.group(1))
            minutes = int(match_hms_colon.group(2))
            seconds = int(match_hms_colon.group(3))
        elif match_ms_double_apostrophe:
            hours = 0
            minutes = int(match_ms_double_apostrophe.group(1))
            seconds = int(match_ms_double_apostrophe.group(2))
        elif match_negative_ms:
            minutes = int(match_negative_ms.group(1))
            seconds = int(match_negative_ms.group(2))
            return -(minutes + seconds / 60)
        elif match_seconds_only:
            return float(match_seconds_only.group(1)) / 60
        elif match_hms:
            hours = int(match_hms.group(1)) if match_hms.group(1) else 0
            minutes = int(match_hms.group(2) or match_hms.group(3)) if (match_hms.group(2) or match_hms.group(3)) else 0
            seconds = int(match_hms.group(4)) if match_hms.group(4) else 0
        else:
            return None

        return hours * 60 + minutes + seconds / 60
