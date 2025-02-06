# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MyketItem(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()
    image_url = scrapy.Field()
    version = scrapy.Field()
    last_update = scrapy.Field()
    num_download = scrapy.Field()
    num_feedback = scrapy.Field()
    size = scrapy.Field()
    price = scrapy.Field()
    kind = scrapy.Field()
    category = scrapy.Field()
    creator = scrapy.Field()
    rating = scrapy.Field()
    rating_5 = scrapy.Field()
    rating_4 = scrapy.Field()
    rating_3 = scrapy.Field()
    rating_2 = scrapy.Field()
    rating_1 = scrapy.Field()
