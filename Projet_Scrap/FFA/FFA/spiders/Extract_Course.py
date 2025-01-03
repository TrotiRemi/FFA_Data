import scrapy
from urllib.parse import urljoin
from itertools import product
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class CompetitionSpider(scrapy.Spider):
    name = "Extract_Course"
    allowed_domains = ["bases.athle.fr"]

    # Configuration personnalisée
    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "DOWNLOAD_DELAY": 1,  # Délais entre les requêtes en secondes
        "AUTOTHROTTLE_ENABLED": True,  # Activer l'autorégulation
        "AUTOTHROTTLE_START_DELAY": 1,  # Délai initial
        "AUTOTHROTTLE_MAX_DELAY": 5,    # Délai maximal
    }

    # Base URL pour générer les variantes
    base_url = "https://bases.athle.fr/asp.net/liste.aspx?frmpostback=true&frmbase=calendrier&frmmode=1&frmespace=0"

    # Paramètres possibles
    saisons = range(1993, 2025)  # De 1993 à 2024 inclus
    niveaux = ["Départemental", "Régional", "National", "International","Mondial","Européen"]
    types = ["Hors+Stade","Cross"]

    # Limite du nombre d'URL
    MAX_URLS = 10

    def start_requests(self):
        # Générer toutes les combinaisons d'URL
        count = 0  # Compteur d'URL
        for saison, niveau, type_ in product(self.saisons, self.niveaux, self.types):
            if count >= self.MAX_URLS:
                self.logger.info("Limite de 100 URLs atteinte, arrêt de la génération d'URL.")
                break  # Arrêter la génération des URLs

            url = f"{self.base_url}&frmsaison={saison}&frmniveau={niveau}&frmtype1={type_}"
            yield scrapy.Request(url, callback=self.parse_pagination)
            count += 1

    def parse_pagination(self, response):
        # Vérifier si la page contient un sélecteur pour plusieurs pages
        page_options = response.xpath('//select[@class="barSelect"]/option/@value').extract()

        if page_options:
            total_pages = max([int(option) for option in page_options]) + 1
            self.logger.info(f"Nombre de pages détecté : {total_pages}")

            for page_number in range(total_pages):
                page_url = f"{response.url}&frmposition={page_number}"
                yield scrapy.Request(page_url, callback=self.parse)
        else:
            # Si pas de pagination, directement traiter la page
            yield from self.parse(response)

    def parse(self, response):
        # Extraire l'année depuis le texte principal
        year_text = response.xpath('//div[@class="mainheaders"]/span/text()').get()

        year = None
        if year_text:  # Vérifier que year_text n'est pas None
            year_match = re.search(r"Année : (\d{4})", year_text)
            if year_match:
                year = year_match.group(1)

        # Sélectionner les lignes correspondant aux compétitions
        rows = response.xpath('//tr[td[contains(@class, "datas")]]')
        for row in rows:
            # Extraire les informations nécessaires
            results_url = row.xpath('./td[1]/a/@href').get()
            full_results_url = urljoin(response.url, results_url) if results_url else None

            competition_date = row.xpath('./td[3]/a/text()').get()
            if competition_date:
                # Si le format est 07-08/05, garder uniquement 07/05
                match = re.match(r"(\d{2})[-/]\d{2}/(\d{2})", competition_date)
                if match:
                    competition_date = f"{match.group(1)}/{match.group(2)}"
                if year:
                    competition_date = f"{competition_date}/{year}"

            yield {
                "results_url": full_results_url,
                "competition_date": competition_date,
                "competition_family": row.xpath('./td[5]/a/text()').get(),
                "competition_name": row.xpath('./td[7]/a/text()').get(),
                "location": row.xpath('./td[9]/text()').get(),
                "ligue": row.xpath('./td[11]/a/text()').get(),
                "department": row.xpath('./td[13]/a/text()').get(),
                "type": row.xpath('./td[15]/text()').get(),
                "level": row.xpath('./td[17]/text()').get(),
            }

    def closed(self, reason):
        # Fonction appelée lorsque le spider se termine
        self.send_email(reason)

    def send_email(self, reason):
        # Configurer les paramètres d'envoi
        sender_email = "rere.locquette@gmail.com"
        receiver_email = "remi.locquette@edu.esiee.fr"
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_user = sender_email  # Utilisez votre adresse email complète ici
        smtp_password = "psng zuef uulb ivif"  # Remplacez par votre mot de passe d'application Gmail

        # Créer le message
        subject = "Rapport de fin de Scrapy"
        body = f"Le spider {self.name} s'est terminé avec le statut : {reason}."
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        try:
            # Envoyer l'email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.sendmail(sender_email, receiver_email, msg.as_string())
            self.logger.info("Email de notification envoyé avec succès.")
        except Exception as e:
            self.logger.error(f"Échec de l'envoi de l'email : {e}")
