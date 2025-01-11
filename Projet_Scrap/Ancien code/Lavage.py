import re
import pandas as pd

df = pd.read_csv("Docker_results.csv")

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

#df.loc[df['competition_name'] == "Départementaux de cross-country cd14", 'distance'] = 8715
#df.loc[(df['rank'] == '1') & (df['athlete'] == 'GALLOT Camille') & (df['distance'] == 3080.0) & (df['competition_name'] == 'Departementaux de cross'), 'time'] = "11'16"

df['distance'] = pd.to_numeric(df['distance'], errors='coerce')
df = df[~((df['rank'].isna() & df['athlete'].isna()) | (df['rank'] == "") | (df['athlete'] == ""))]
df = df[df['rank'].str.len() <= 10]
df['department'] = df['department'].fillna(0)
df['club'] = df['club'].replace(r'^\s*$', None, regex=True)
df['club'] = df['club'].fillna("No Club")
df = df.drop_duplicates()
df = df[df['athlete'].notna() & (df['athlete'] != "")]
df['Minute_Time'] = df['time'].apply(convert_to_minutes)
df['vitesse'] = (df['distance'] / 1000) / (df['Minute_Time'] / 60)
df.loc[df['vitesse'] == float('inf'), 'vitesse'] = 0

df['level'] = df['level'].replace({
    'Rég': 'Régional',
    'Nat': 'National',
    'Int': 'Interrégional',
    'Dép': 'Départemental'
})

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

# Remplacement de la colonne Ligue par les abréviations
df["ligue_complet"] = df["ligue"].map(ligue_mapping)

output_csv = 'Docker_results_laver.csv'
df.to_csv(output_csv, index=False, encoding='utf-8')
