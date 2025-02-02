# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import json


class MiketScraperPipeline:
    def open_spider(self, spider):
        self.f = open('items.csv', 'w')

    def close_spider(self, spider):
        self.f.close()

    def process_item(self, item, spider):
        json.dump(ItemAdapter(item).asdict(), self.f)
        self.f.write('\n')
        return item
