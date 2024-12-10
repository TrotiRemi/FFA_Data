import scrapy

class ResultsSpider(scrapy.Spider):
    name = "results_final"
    allowed_domains = ["kikourou.net"]
    start_urls = ["https://www.kikourou.net/resultats/?annee=2024"]

    def parse(self, response):
        # Sélection des blocs de résultats
        results = response.xpath('//ul[@id="listresult"]/li')
        for result in results:
            yield {
                "date": result.xpath('text()').re_first(r"\[(\d{2}/\d{2}/\d{4})\]"),
                "name": result.xpath('.//a[2]/text()').get(),
                "num_classified": result.xpath('text()').re_first(r"(\d+) classés"),
                "result_url": response.urljoin(result.xpath('.//a[1]/@href').get()),
                "course_url": response.urljoin(result.xpath('.//a[2]/@href').get()),
            }

        # Pagination (si disponible)
        next_page = response.xpath('//a[@rel="next"]/@href').get()
        if next_page:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)