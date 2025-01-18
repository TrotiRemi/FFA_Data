import scrapy

class CompetitionResultItem(scrapy.Item):
    rank = scrapy.Field()
    time = scrapy.Field()
    athlete = scrapy.Field()
    club = scrapy.Field()
    category = scrapy.Field()
    competition_date = scrapy.Field()
    competition_name = scrapy.Field()
    location = scrapy.Field()
    ligue = scrapy.Field()
    department = scrapy.Field()
    type = scrapy.Field()
    level = scrapy.Field()
    full_line = scrapy.Field()
    distance = scrapy.Field()
    Minute_Time = scrapy.Field()
    ligue = scrapy.Field()  # Ajout du champ ligue_complet
    vitesse = scrapy.Field()        # Ajout du champ vitesse
    type_course = scrapy.Field()
