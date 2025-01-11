import re
from pymongo import MongoClient

# Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["my_database"]
collection = db["docker_results"]

# Fonction pour convertir le temps en minutes
def convert_to_minutes(time_str):
    match_hms_colon = re.match(r"^(\d+):(\d+):(\d+)$", time_str)
    match_ms_double_apostrophe = re.match(r"^(\d+)'(\d+)''$", time_str)
    match_negative_ms = re.match(r"^- \((\d+)'(\d+)''\)$", time_str)
    match_seconds_only = re.match(r"^(\d+)''$", time_str)
    match_distance = re.match(r"^(\d+)km(\d+)m$", time_str)

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
        return minutes + seconds / 60
    elif match_seconds_only:
        return 0
    elif match_distance:
        return 0
    else:
        match_hms = re.match(r"(?:(\d+)h)?(?:(\d+)'|(\d+):)?(\d+)?", time_str)
        if match_hms:
            hours = int(match_hms.group(1)) if match_hms.group(1) else 0
            minutes = int(match_hms.group(2) or match_hms.group(3)) if (match_hms.group(2) or match_hms.group(3)) else 0
            seconds = int(match_hms.group(4)) if match_hms.group(4) else 0
        else:
            return None

    total_minutes = hours * 60 + minutes + seconds / 60
    return total_minutes

# Mapping des niveaux
level_mapping = {
    'Rég': 'Régional',
    'Nat': 'National',
    'Int': 'Interrégional',
    'Dép': 'Départemental'
}

# Mapping des ligues
ligue_mapping = {
    "NORM": "Normandie",
    "NOR": "Normandie",
    "BFC": "Bourgogne-Franche-Comté",
    "OCC": "Occitanie",
    "N-A": "Nouvelle-Aquitaine",
    "PAC": "Provence-Alpes-Côte d'Azur",
    "CEN": "Centre-Val de Loire",
    "P-L": "Pays de la Loire",
    "H-F": "Hauts-de-France",
    "IDF": "Île-de-France",
    "I-F": "Île-de-France",
    "ARA": "Auvergne-Rhône-Alpes",
    "BRE": "Bretagne",
    "GE": "Grand Est",
    "G-E": "Grand Est",
    "NAQ": "Nouvelle-Aquitaine",
    "COR": "Corse",
    "GUY": "Guyane",
    "GUA": "Guadeloupe",
    "MAR": "Martinique",
    "REU": "La Réunion",
    "MAY": "Mayotte"
}

# Itération sur les documents de la collection
for doc in collection.find():
    updates = {}

    # Nettoyage de la distance
    if 'distance' in doc:
        try:
            updates['distance'] = float(doc['distance'])
        except (ValueError, TypeError):
            updates['distance'] = None

    # Conversion du temps en minutes
    if 'time' in doc:
        updates['Minute_Time'] = convert_to_minutes(doc['time'])

    # Calcul de la vitesse
    if 'distance' in updates and updates['Minute_Time']:
        if updates['Minute_Time'] > 0:
            updates['vitesse'] = (updates['distance'] / 1000) / (updates['Minute_Time'] / 60)
        else:
            updates['vitesse'] = 0

    # Nettoyage du niveau
    if 'level' in doc:
        updates['level'] = level_mapping.get(doc['level'], doc['level'])

    # Nettoyage du club
    if 'club' in doc:
        if not doc['club'] or doc['club'].strip() == "":
            updates['club'] = "No Club"

    # Remplacement des abréviations de ligue
    if 'ligue' in doc:
        updates['ligue_complet'] = ligue_mapping.get(doc['ligue'], doc['ligue'])

    # Application des mises à jour
    if updates:
        collection.update_one({'_id': doc['_id']}, {'$set': updates})

print("Les données ont été nettoyées directement dans la base MongoDB.")
