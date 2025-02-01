# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MiketItem(scrapy.Item):
    name = scrapy.Field()
    image_url = scrapy.Field()
    version = scrapy.Field()
    last_update = scrapy.Field()
    num_download = scrapy.Field()
    rating = scrapy.Field()
    num_feedback = scrapy.Field()
    size = scrapy.Field()
    kind = scrapy.Field()
    category = scrapy.Field()
    creator = scrapy.Field()
    ratings_percentage = scrapy.Field()
