import scrapy


class ResultsSpider(scrapy.Spider):
    name = "results_final2"
    allowed_domains = ["kikourou.net"]
    start_urls = ["https://www.kikourou.net/resultats/?annee=2024"]

    def parse(self, response):
        # Sélectionner le bloc contenant les résultats
        results_section = response.xpath('//h2[text()="Courses avec résultats sur le web"]/following-sibling::ul/li')
        
        for result in results_section:
            yield {
                "date": result.xpath('text()').re_first(r"\[(\d{2}/\d{2}/\d{4})\]"),
                "name": result.xpath('.//a[2]/text()').get(),
                "submitted_by": result.xpath('.//a[last()]/text()').get(),
                "result_url": result.xpath('.//a[1]/@href').get(),
                "course_url": response.urljoin(result.xpath('.//a[2]/@href').get()),
            }

        # Pagination (si disponible)
        next_page = response.xpath('//a[@rel="next"]/@href').get()
        if next_page:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)
