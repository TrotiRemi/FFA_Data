import scrapy
from urllib.parse import urljoin
from itertools import product

class CompetitionSpider(scrapy.Spider):
    name = "FFA1"
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
    niveaux = ["Départemental", "Régional", "National", "International"]
    types = ["Hors", "Stade", "Marche", "Route", "Piste", "Salle", "Cross"]

    def start_requests(self):
        # Générer toutes les combinaisons d'URL
        for saison, niveau, type_ in product(self.saisons, self.niveaux, self.types):
            url = f"{self.base_url}&frmsaison={saison}&frmniveau={niveau}&frmtype1={type_}"
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        # Sélectionner les lignes correspondant aux compétitions
        rows = response.xpath('//tr[td[contains(@class, "datas")]]')
        for row in rows:
            # Extraire les informations nécessaires
            results_url = row.xpath('./td[1]/a/@href').get()
            full_results_url = urljoin(response.url, results_url) if results_url else None

            yield {
                "results_url": full_results_url,
                "competition_date": row.xpath('./td[3]/a/text()').get(),
                "competition_family": row.xpath('./td[5]/a/text()').get(),
                "competition_name": row.xpath('./td[7]/a/text()').get(),
                "location": row.xpath('./td[9]/text()').get(),
                "ligue": row.xpath('./td[11]/a/text()').get(),
                "department": row.xpath('./td[13]/a/text()').get(),
                "type": row.xpath('./td[15]/text()').get(),
                "level": row.xpath('./td[17]/text()').get(),
            }
