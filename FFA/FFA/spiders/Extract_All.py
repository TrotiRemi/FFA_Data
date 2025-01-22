import scrapy
from urllib.parse import urljoin
from itertools import product
import re
from FFA.items import CompetitionResultItem
from scrapy.exceptions import CloseSpider


class CompetitionAndResultsSpider(scrapy.Spider):
    name = "competition_results"
    allowed_domains = ["bases.athle.fr"]
    base_url = "https://bases.athle.fr/asp.net/liste.aspx?frmpostback=true&frmbase=calendrier&frmmode=1&frmespace=0"

    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "DOWNLOAD_DELAY": 1,
        "FEEDS": {
            "results2.csv": {
                "format": "csv",
                "fields": [
                    "rank","athlete","club","category","Minute_Time","distance","vitesse",
                    "competition_name","competition_date","type_course","location","department","ligue","type","level","full_line","time"
                ],
                "append": True,
            },
        },
    }

    saisons = range(2020, 2026)
    niveaux = ["Départemental", "Régional", "National", "Interrégional"]
    types = ["Hors+Stade","Cross"]

    result_count = 0
    max_results = 10000

    def start_requests(self):
        for saison, niveau, type_ in product(self.saisons, self.niveaux, self.types):
            if self.result_count >= self.max_results:
                self.logger.info(f"Limite de {self.max_results} résultats atteinte. Arrêt du spider.")
                raise CloseSpider(f"Limite de {self.max_results} résultats atteinte.")
            url = f"{self.base_url}&frmsaison={saison}&frmniveau={niveau}&frmtype1={type_}"
            yield scrapy.Request(
                url, 
                callback=self.parse_pagination, 
                meta={"competition_date": saison, "type_course": type_}  # Ajout du type_course dans les métadonnées
            )

    def parse_pagination(self, response):
        if self.result_count >= self.max_results:
            self.logger.info(f"Limite de {self.max_results} résultats atteinte. Arrêt du spider.")
            raise CloseSpider(f"Limite de {self.max_results} résultats atteinte.")
        
        page_options = response.xpath('//select[@class="barSelect"]/option/@value').extract()
        if page_options:
            total_pages = max([int(option) for option in page_options])
            for page_number in range(total_pages):
                if self.result_count >= self.max_results:
                    self.logger.info(f"Limite de {self.max_results} résultats atteinte. Arrêt du spider.")
                    raise CloseSpider(f"Limite de {self.max_results} résultats atteinte.")
                page_url = f"{response.url}&frmposition={page_number}"
                yield scrapy.Request(page_url, callback=self.parse_competitions, meta=response.meta)
        else:
            yield from self.parse_competitions(response)

    def parse_competitions(self, response):
        if self.result_count >= self.max_results:
            self.logger.info(f"Limite de {self.max_results} résultats atteinte. Arrêt du spider.")
            raise CloseSpider(f"Limite de {self.max_results} résultats atteinte.")
        
        competition_date = response.meta["competition_date"]
        type_course = response.meta["type_course"]  # Récupération du type_course
        rows = response.xpath('//tr[td[contains(@class, "datas")]]')
        for row in rows:
            if self.result_count >= self.max_results:
                self.logger.info(f"Limite de {self.max_results} résultats atteinte. Arrêt du spider.")
                raise CloseSpider(f"Limite de {self.max_results} résultats atteinte.")
            
            results_url = urljoin(response.url, row.xpath('./td[1]/a/@href').get())
            competition = {
                "results_url": results_url,
                "competition_date": competition_date,
                "competition_name": row.xpath('./td[7]/a/text()').get(),
                "location": row.xpath('./td[9]/text()').get(),
                "ligue": row.xpath('./td[11]/a/text()').get(),
                "department": row.xpath('./td[13]/a/text()').get(),
                "type": row.xpath('./td[15]/text()').get(),
                "level": row.xpath('./td[17]/text()').get(),
                "type_course": type_course  # Ajout du type_course
            }
            if results_url:
                yield scrapy.Request(results_url, callback=self.parse_results, meta={"competition": competition})

    def parse_results(self, response):
        if self.result_count >= self.max_results:
            self.logger.info(f"Limite de {self.max_results} résultats atteinte. Arrêt du spider.")
            raise CloseSpider(f"Limite de {self.max_results} résultats atteinte.")

        # Extraire la date de la compétition à partir de "mainheaders"
        mainheaders_text = response.xpath('//div[contains(@class, "mainheaders")]/text()').get()
        competition_date = self.extract_date(mainheaders_text) if mainheaders_text else None

        competition = response.meta["competition"]
        if competition_date:
            competition["competition_date"] = competition_date

        rows = response.xpath('//tr')
        current_full_line = None

        for row in rows:
            if self.result_count >= self.max_results:
                self.logger.info(f"Limite de {self.max_results} résultats atteinte. Arrêt du spider.")
                raise CloseSpider(f"Limite de {self.max_results} résultats atteinte.")

            # Identifier les sous-courses
            distance_element = row.xpath('.//div[contains(@class, "subheaders")]/text()').get()
            if distance_element:
                current_full_line = distance_element.strip()
                continue

            # Identification des colonnes des coureurs
            columns = row.xpath('./td')
            if len(columns) < 13:
                continue

            # Extraction des informations
            rank = columns[0].xpath('text()').get()
            time = self.extract_time(columns[2])  # Méthode dédiée pour extraire le temps
            athlete = columns[4].xpath('a/text()').get() or columns[4].xpath('text()').get()
            club = columns[6].xpath('a/text()').get() or columns[6].xpath('text()').get()
            category = columns[12].xpath('a/text()').get()

            # Création de l'objet CompetitionResultItem
            result = CompetitionResultItem(
                full_line=current_full_line,
                rank=rank.strip() if rank else None,
                time=time,
                athlete=athlete.strip() if athlete else "Inconnu",
                club=club.strip() if club and club.strip() != "&nbsp;" else "No Club",
                category=category.strip() if category else None,
                competition_date=competition["competition_date"],
                competition_name=competition["competition_name"],
                location=competition["location"],
                ligue=competition["ligue"],
                department=competition["department"],
                type=competition["type"],
                level=competition["level"],
                type_course=competition["type_course"],  # Ajout du type_course
            )

            self.result_count += 1
            yield result

        # Pagination des résultats
        # Rechercher le nombre total de pages à partir du code HTML source
        pagination_info = response.xpath('//select[@class="barSelect"]/option[contains(text(), "Page")]/text()').get()
        if pagination_info:
            # Extraire le total de pages (par exemple, "001/060")
            match_pages = re.search(r"\d+/\d+", pagination_info)
            if match_pages:
                current_page, total_pages = map(int, match_pages.group().split('/'))
                if current_page < total_pages:  # Si la page actuelle est inférieure au total
                    next_page_url = f"{response.url.split('&frmposition=')[0]}&frmposition={current_page}"
                    self.logger.info(f"Navigation vers la page suivante des résultats : {next_page_url}")
                    yield scrapy.Request(next_page_url, callback=self.parse_results, meta={"competition": competition})

    def extract_time(self, column):
        """
        Méthode robuste pour extraire le temps d'une colonne donnée.
        """
        # Extraire tous les textes possibles dans la cellule
        all_texts = column.xpath('.//text()').getall()

        # Filtrer et nettoyer les textes pour ignorer les espaces inutiles
        cleaned_texts = [text.strip() for text in all_texts if text.strip()]

        if cleaned_texts:
            # Retourner le texte joint par un espace si plusieurs éléments existent
            return " ".join(cleaned_texts)
        return None

    def extract_date(self, mainheaders_text):
        """
        Extrait et formate la date de la course à partir du texte du header principal.
        """
        match = re.search(r"(\d{2}/\d{2}/\d{2})", mainheaders_text)
        if match:
            date_str = match.group(1)  # Exemple : "01/09/24"
            day, month, year = date_str.split("/")
            year = f"20{year}"  # Ajouter "20" au début de l'année
            formatted_date = f"{day}/{month}/{year}"  # Reformater en J/M/A
            return formatted_date
        return None
