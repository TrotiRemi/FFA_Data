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
            "results.csv": {
                "format": "csv",
                "fields": [
                    "rank","athlete","sex","club","category","Minute_Time","distance","vitesse",
                    "competition_name","competition_date","location","department","ligue_complet","type","level","full_line","time"
                ],
                "overwrite": True,
            },
        },
    }

    saisons = range(2020, 2026)
    niveaux = ["Départemental", "Régional", "National", "International"]
    types = ["Hors+Stade","Cross"]

    result_count = 0
    max_results = 10000000000

    def start_requests(self):
        for saison, niveau, type_ in product(self.saisons, self.niveaux, self.types):
            if self.result_count >= self.max_results:
                self.logger.info(f"Limite de {self.max_results} résultats atteinte. Arrêt du spider.")
                raise CloseSpider(f"Limite de {self.max_results} résultats atteinte.")
            url = f"{self.base_url}&frmsaison={saison}&frmniveau={niveau}&frmtype1={type_}"
            yield scrapy.Request(url, callback=self.parse_pagination, meta={"competition_date": saison})

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
            club = columns[6].xpath('text()').get()
            category = columns[12].xpath('a/text()').get()

            # Création de l'objet CompetitionResultItem
            result = CompetitionResultItem(
                full_line=current_full_line,
                rank=rank.strip() if rank else None,
                time=time,  # Utilisation du temps extrait
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
            )

            self.result_count += 1
            yield result

    def extract_time(self, column):
        """
        Méthode robuste pour extraire le temps d'une colonne donnée.
        """
        time = (
            column.xpath('b/text()').get() or  # Priorité 1 : <b>
            column.xpath('u/b/text()').get() or  # Priorité 2 : <u><b>
            column.xpath('u/text()').get() or  # Priorité 3 : <u>
            column.xpath('text()').get()       # Priorité 4 : texte brut
        )

        if time:
            time = time.strip()
            return time  # Retourne le temps tel quel pour être traité plus tard
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
