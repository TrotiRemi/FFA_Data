import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# URL de la page principale
main_url = "https://www.athle.fr/asp.net/main.html/html.aspx?htmlid=5255"

# Fonction pour récupérer les URL des niveaux
def get_level_urls(main_url):
    try:
        response = requests.get(main_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        level_urls = {}
        categories = ['Cross', 'Salle', 'Stade', 'Hors Stade', 'Marche Route']
        for category in categories:
            level_urls[category] = {}
            table = soup.find('table', {'style': 'text-align: center; margin-top: 5px;'})
            rows = table.find_all('tr')[1:]  # Ignorer la ligne d'en-tête
            for row in rows:
                cells = row.find_all('td')
                if len(cells) == 5:  # Chaque cellule correspond à un niveau
                    levels = ['Mondial', 'National', 'Interrégional', 'Régional', 'Départemental']
                    for i, cell in enumerate(cells):
                        if cell.find('div', {'class': 'boite'}):
                            url = cell.find('div', {'class': 'boite'}).get('onclick').split("'")[1]
                            level_urls[category][levels[i]] = url
        return level_urls
    except Exception as e:
        print(f"Erreur lors de la récupération des URLs des niveaux : {e}")
        return {}

# Fonction pour scraper les résultats d'une URL spécifique
def scrape_competitions(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        rows = soup.select('tr.listResCom')  # Modifier pour capturer les lignes spécifiques
        competitions = []
        for row in rows:
            competitions.append({
                "competition_date": row.select_one('td:nth-child(3) a').text.strip() if row.select_one('td:nth-child(3) a') else None,
                "competition_type": row.select_one('td:nth-child(5) a').text.strip() if row.select_one('td:nth-child(5) a') else None,
                "competition_name": row.select_one('td:nth-child(7) a').text.strip() if row.select_one('td:nth-child(7) a') else None,
                "location": row.select_one('td:nth-child(9)').text.strip() if row.select_one('td:nth-child(9)') else None,
                "ligue": row.select_one('td:nth-child(11) a').text.strip() if row.select_one('td:nth-child(11) a') else None,
                "department": row.select_one('td:nth-child(13) a').text.strip() if row.select_one('td:nth-child(13) a') else None,
                "type": row.select_one('td:nth-child(15)').text.strip() if row.select_one('td:nth-child(15)') else None,
                "level": row.select_one('td:nth-child(17)').text.strip() if row.select_one('td:nth-child(17)') else None,
            })
        return competitions
    except Exception as e:
        print(f"Erreur lors du scraping des compétitions : {e}")
        return []

# Récupérer les URLs des niveaux
level_urls = get_level_urls(main_url)

# Récupérer toutes les compétitions pour chaque catégorie et niveau
all_competitions = []
for category, levels in level_urls.items():
    for level, url in levels.items():
        print(f"Scraping {category} - {level} : {url}")
        competitions = scrape_competitions(url)
        for competition in competitions:
            competition['category'] = category
            competition['level'] = level
        all_competitions.extend(competitions)

# Convertir les résultats en DataFrame
df = pd.DataFrame(all_competitions)

# Sauvegarder les résultats dans un fichier CSV
output_csv = 'all_competitions.csv'
df.to_csv(output_csv, index=False, encoding='utf-8')

print(f"Toutes les compétitions sauvegardées dans {output_csv}")
