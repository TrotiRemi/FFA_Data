import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

file_name = 'concatenated_FFA.csv'
data = pd.read_csv(file_name)

def extract_date_from_header(soup):
    header_element = soup.select_one('div.mainheaders')
    if header_element:
        match = re.search(r'(\d{2}/\d{2}/\d{2})', header_element.text)
        if match:
            return match.group(1) 
    return None

def extract_page_numbers(soup):
    """
    Extrait les numéros de pages disponibles dans le sélecteur.
    """
    options = soup.select('select.barSelect option')
    page_numbers = []
    for option in options:
        value = option.get('value')
        if value and value.isdigit():
            page_numbers.append(int(value))
    return sorted(set(page_numbers))

def scrape_page_with_distances(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        competition_date = extract_date_from_header(soup)

        results = []
        current_distance = None

        rows = soup.select('tr')
        for row in rows:
            distance_element = row.select_one('div.subheaders')
            if distance_element:
                match = re.search(r'\|\s*(\d+)\s*m', distance_element.text)
                if match:
                    current_distance = int(match.group(1))
                    continue 

            columns = row.find_all('td')
            if len(columns) > 1 and current_distance is not None: 
                results.append({
                    "rank": columns[0].text.strip() if len(columns) > 0 else None,
                    "time": columns[2].text.strip() if len(columns) > 2 else None,
                    "athlete": columns[4].text.strip() if len(columns) > 4 else None,
                    "club": columns[6].text.strip() if len(columns) > 6 else None,
                    "category": columns[12].text.strip() if len(columns) > 12 else None,
                    "distance": current_distance, 
                    "date": competition_date,
                })

        return results
    except Exception as e:
        print(f"Erreur lors du scraping de l'URL {url}: {e}")
        return []

def scrape_url_with_pagination(base_url, max_results):
    all_results = []
    try:
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        page_numbers = extract_page_numbers(soup)
        print(f"Pages trouvées: {page_numbers}")

        for page_number in page_numbers:
            if len(all_results) >= max_results:
                break 
            page_url = f"{base_url}&frmposition={page_number}"
            print(f"Scraping URL: {page_url}")
            scraped_data = scrape_page_with_distances(page_url)
            all_results.extend(scraped_data)
            if len(all_results) >= max_results:
                break 

    except Exception as e:
        print(f"Erreur lors du traitement de l'URL {base_url}: {e}")

    return all_results[:max_results]

all_results = []
MAX_RESULTS = 1000000
for index, row in data.iterrows():
    if len(all_results) >= MAX_RESULTS:
        break 
    url = row['results_url']
    print(f"Traitement de l'URL: {url}")

    scraped_data = scrape_url_with_pagination(url, MAX_RESULTS - len(all_results))

    for result in scraped_data:
        result.update({
            "competition_type": row['competition_type'],
            "competition_name": row['competition_name'],
            "location": row['location'],
            "ligue": row['ligue'],
            "department": row['department'],
            "type": row['type'],
            "level": row['level'],
        })
        all_results.append(result)
        if len(all_results) >= MAX_RESULTS:
            break  
df = pd.DataFrame(all_results)

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

df.loc[(df['rank'] == '1') & (df['athlete'] == 'GALLOT Camille') & (df['distance'] == 3080.0) & (df['competition_name'] == 'Departementaux de cross'), 'time'] = "11'16"
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


output_csv = 'unlimited_results.csv'
df.to_csv(output_csv, index=False, encoding='utf-8')

print(f"Résultats sauvegardés dans {output_csv}")
