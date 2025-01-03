import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import pymongo
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

# Récupérer l'URI MongoDB depuis l'environnement
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/CourseDatabase")
client = pymongo.MongoClient(MONGO_URI)
db = client["CoureurDatabase"]
collection = db["Results"]

# Configuration de l'email
def send_email(subject, body):
    sender_email = "rere.locquette@gmail.com"
    receiver_email = "remi.locquette@edu.esiee.fr"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = sender_email
    smtp_password = "psng zuef uulb ivif"  # Remplacez par votre mot de passe d'application Gmail

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("Email envoyé avec succès.")
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email : {e}")

file_name = 'Course_pages.csv'
data = pd.read_csv(file_name)
total_urls = len(data)
failed_urls = []

def scrape_page_with_full_lines_and_details(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        competition_date = None  # Initialiser la date
        header_element = soup.select_one('div.mainheaders')
        if header_element:
            match = re.search(r'(\d{2}/\d{2}/\d{2})', header_element.text)
            if match:
                competition_date = match.group(1)

        results = []
        current_full_line = None
        rows = soup.select('tr')

        for row in rows:
            # Identifier un nouveau bandeau
            distance_element = row.select_one('div.subheaders')
            if distance_element:
                current_full_line = distance_element.text.strip()
                continue

            # Extraire les données des coureurs
            columns = row.find_all('td')
            if len(columns) > 1 and current_full_line:
                results.append({
                    "full_line": current_full_line,  # Ligne actuelle
                    "rank": columns[0].text.strip() if len(columns) > 0 else None,
                    "time": columns[2].text.strip() if len(columns) > 2 else None,
                    "athlete": columns[4].text.strip() if len(columns) > 4 else None,
                    "club": columns[6].text.strip() if len(columns) > 6 else None,
                    "category": columns[12].text.strip() if len(columns) > 12 else None,
                    "date": competition_date,
                })

        return results
    except Exception as e:
        print(f"Erreur lors du scraping de la page {url} : {e}")
        failed_urls.append({"url": url, "error": str(e)})
        return []

def scrape_url_with_pagination(base_url, max_results):
    all_results = []
    try:
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extraire les pages de pagination
        page_numbers = [1]  # Initialiser avec la première page
        options = soup.select('select.barSelect option')
        for option in options:
            value = option.get('value')
            if value and value.isdigit():
                page_numbers.append(int(value))
        page_numbers = sorted(set(page_numbers))

        for page_number in page_numbers:
            if len(all_results) >= max_results:
                break
            page_url = f"{base_url}&frmposition={page_number}"
            scraped_data = scrape_page_with_full_lines_and_details(page_url)
            all_results.extend(scraped_data)
            if len(all_results) >= max_results:
                break

    except Exception as e:
        print(f"Erreur lors de la pagination pour l'URL {base_url} : {e}")
        failed_urls.append({"url": base_url, "error": str(e)})

    return all_results[:max_results]

try:
    MAX_RESULTS = 50000
    progress_threshold = 0.1  # 10%
    next_progress = int(total_urls * progress_threshold)

    # URL de démarrage (vide signifie commencer depuis le début)
    start_url = "https://bases.athle.fr/asp.net/liste.aspx?frmbase=resultats&frmmode=1&frmespace=0&frmcompetition=000004"
    start_index = 0

    # Rechercher l'indice de l'URL de départ si spécifié
    if start_url:
        if start_url in data['results_url'].values:
            start_index = data[data['results_url'] == start_url].index[0]
        else:
            print(f"L'URL de départ {start_url} n'existe pas dans le fichier CSV. Début du traitement depuis le début.")
            start_index = 0

    last_url_processed = None  # Pour garder en mémoire la dernière URL traitée
    total_inserted = 0  # Compteur pour les insertions

    for index, row in data.iterrows():
        if index < start_index:  # Ignorer les URL avant l'index de démarrage
            continue

        # Arrêter si le nombre maximum de résultats est atteint
        if total_inserted >= MAX_RESULTS:
            print(f"Nombre maximum de résultats atteints : {total_inserted}")
            break

        url = row['results_url']
        last_url_processed = url  # Mettre à jour la dernière URL traitée
        try:
            scraped_data = scrape_url_with_pagination(url, MAX_RESULTS - total_inserted)

            for result in scraped_data:
                result.update({
                    "competition_type": row['type'],
                    "competition_name": row['competition_name'],
                    "location": row['location'],
                    "ligue": row['ligue'],
                    "department": row['department'],
                    "type": row['type'],
                    "level": row['level'],
                })

                # Vérification pour éviter les doublons avant insertion
                if not collection.find_one(result):
                    collection.insert_one(result)
                    total_inserted += 1

                # Arrêter si le nombre maximum de résultats est atteint
                if total_inserted >= MAX_RESULTS:
                    print(f"Nombre maximum de résultats atteints : {total_inserted}")
                    break

            # Arrêter après le traitement de cette URL si le maximum est atteint
            if total_inserted >= MAX_RESULTS:
                break

        except Exception as e:
            print(f"Erreur lors du traitement de l'URL {url} : {e}")
            failed_urls.append({"url": url, "error": str(e)})

        # Vérifier la progression
        if (index + 1) >= next_progress:
            percentage = int(((index + 1) / total_urls) * 100)
            print(f"Progression : {percentage}%")
            next_progress += int(total_urls * progress_threshold)

    if failed_urls:
        for failed_url in failed_urls:
            if not collection.find_one({"url": failed_url["url"], "error": failed_url["error"]}):
                collection.insert_one(failed_url)
        print(f"{len(failed_urls)} URL échouées insérées dans MongoDB.")

    # Afficher la dernière URL traitée
    print(f"Dernière URL traitée : {last_url_processed}")

except Exception as e:
    # Afficher la dernière URL traitée même en cas d'erreur critique
    print(f"Dernière URL traitée avant l'erreur : {last_url_processed}")
    send_email("Erreur critique", f"Le script s'est arrêté en raison de l'erreur suivante : {e}")
