import scrapy
from urllib.parse import urljoin

class CompetitionSpider(scrapy.Spider):
    name = "FFA2"
    allowed_domains = ["bases.athle.com"]
    start_urls = ["https://bases.athle.fr/asp.net/liste.aspx?frmpostback=true&frmbase=calendrier&frmmode=1&frmespace=0&frmsaison=2024&frmtype1=Cross&frmtype2=&frmtype3=&frmtype4=&frmniveau=National&frmniveaulab=&frmligue=&frmdepartement=&frmepreuve=&frmdate_j1=&frmdate_m1=&frmdate_a1=&frmdate_j2=&frmdate_m2=&frmdate_a2="]

    def parse(self, response):
        # Sélection de la ligne spécifique
        rows = response.xpath('//tr[contains(td/@class, "listResCom")]')
        for row in rows:
            results_url = row.xpath('.//td[1]/a/@href').get()
            # Utilisation de urljoin pour compléter l'URL relative
            full_results_url = urljoin("https://bases.athle.fr/", results_url)
            
            yield {
                "results_url": full_results_url,
                "competition_date": row.xpath('.//td[3]/a/text()').get(),
                "competition_type": row.xpath('.//td[5]/a/text()').get(),
                "competition_name": row.xpath('.//td[7]/a/text()').get(),
                "location": row.xpath('.//td[9]/text()').get(),
                "ligue": row.xpath('.//td[11]/a/text()').get(),
                "department": row.xpath('.//td[13]/a/text()').get(),
                "type": row.xpath('.//td[15]/text()').get(),
                "level": row.xpath('.//td[17]/text()').get(),
            }
