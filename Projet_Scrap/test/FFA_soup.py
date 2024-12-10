import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# Charger le fichier CSV
file_name = 'concatenated_FFA.csv'
data = pd.read_csv(file_name)

# Fonction pour extraire la date du titre
def extract_date_from_title(soup):
    title_element = soup.select_one('div.mainheaders')
    if title_element:
        match = re.search(r'(\d{2}/\d{2}/\d{2})', title_element.text)
        if match:
            return match.group(1)  # Retourne la date extraite
    return None

# Fonction pour extraire les numéros de pages
def extract_page_numbers(soup):
    """
    Extrait les numéros de pages disponibles dans le sélecteur.
    """
    options = soup.select('select.barSelect option')
    page_numbers = []
    for option in options:
        value = option.get('value')
        if value and value.isdigit():  # Vérifie que la valeur est un numéro
            page_numbers.append(int(value))
    return sorted(set(page_numbers))  # Supprime les doublons et trie les numéros

# Fonction pour scraper une page spécifique
def scrape_page(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extraire la date
        competition_date = extract_date_from_title(soup)

        # Extraire les distances des courses
        distance_rows = soup.select('tr div.subheaders')
        distances = [
            re.search(r'(\d+)\s?m', row.text.strip()).group(1)
            if re.search(r'(\d+)\s?m', row.text.strip()) else None
            for row in distance_rows
        ]

        # Extraire les résultats
        rows = soup.select('tr')
        results = []
        for row in rows:
            columns = row.find_all('td')
            if len(columns) > 1:  # Éviter les lignes vides ou non pertinentes
                results.append({
                    "rank": columns[0].text.strip() if len(columns) > 0 else None,
                    "time": columns[2].text.strip() if len(columns) > 2 else None,
                    "athlete": columns[4].text.strip() if len(columns) > 4 else None,
                    "club": columns[6].text.strip() if len(columns) > 6 else None,
                    "category": columns[12].text.strip() if len(columns) > 12 else None,
                    "distance": distances[0] if distances else None,  # Distance associée
                })

        return {
            "competition_date": competition_date,
            "results": results,
        }
    except Exception as e:
        print(f"Erreur lors du scraping de l'URL {url}: {e}")
        return {"competition_date": None, "results": []}

# Fonction pour scraper toutes les pages avec des numéros
def scrape_url_with_pagination(base_url):
    all_results = []
    try:
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extraire les numéros de pages
        page_numbers = extract_page_numbers(soup)
        print(f"Pages trouvées: {page_numbers}")

        for page_number in page_numbers:
            page_url = f"{base_url}&frmposition={page_number}"
            print(f"Scraping URL: {page_url}")
            scraped_data = scrape_page(page_url)
            all_results.extend(scraped_data['results'])
    except Exception as e:
        print(f"Erreur lors du traitement de l'URL {base_url}: {e}")

    return all_results

# Parcourir toutes les URLs et scraper les données
all_results = []
processed_count = 0  # Compteur de résultats

for index, row in data.iterrows():
    if processed_count >= 1000:  # Limiter à 1000 données
        break
    url = row['results_url']
    print(f"Traitement de l'URL: {url}")

    # Scraper toutes les pages pour l'URL actuelle
    scraped_data = scrape_url_with_pagination(url)

    for result in scraped_data:
        # Ajouter les colonnes globales pour chaque course
        result.update({
            "competition_date": result.get("competition_date", row['competition_date']),
            "competition_type": row['competition_type'],
            "competition_name": row['competition_name'],
            "location": row['location'],
            "ligue": row['ligue'],
            "department": row['department'],
            "type": row['type'],
            "level": row['level'],
        })
        all_results.append(result)
    processed_count += 1

# Convertir les résultats en DataFrame
df = pd.DataFrame(all_results)

# Nettoyer les données
df = df[~((df['rank'].isna() & df['athlete'].isna()) | (df['rank'] == "") | (df['athlete'] == ""))]
df = df[df['rank'].str.len() <= 10]
df['department'] = df['department'].fillna(0)
df['club'] = df['club'].fillna("No Club")
df=df.drop_duplicates()
# Sauvegarder les résultats dans un fichier CSV
output_csv = '1001_with_correct_pagination_numbers.csv'
df.to_csv(output_csv, index=False, encoding='utf-8')

print(f"Résultats sauvegardés dans {output_csv}")
