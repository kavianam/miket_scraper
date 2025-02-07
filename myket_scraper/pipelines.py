# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from scrapy.exporters import CsvItemExporter
import sqlite3


class CSVPipeline:
    def open_spider(self, spider):
        self.file = open('output.csv', 'wb')
        self.exporter = CsvItemExporter(self.file, encoding='utf-8')
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class SQLitePipeline:

    def open_spider(self, spider):
        # Connect to the SQLite database or create it
        self.connection = sqlite3.connect('myket.db')
        self.cursor = self.connection.cursor()
        # Create a table if it doesn't exist
        self.cursor.execute('''
            create table IF NOT EXISTS app
            (
                name         TEXT PRIMARY KEY,
                url          TEXT,
                image_url    TEXT,
                version      TEXT,
                last_update  TEXT,
                num_download integer,
                num_feedback integer,
                size         integer,
                price        integer,
                kind         TEXT,
                category     TEXT,
                creator      TEXT,
                rating       REAL,
                rating_5     integer,
                rating_4     integer,
                rating_3     integer,
                rating_2     integer,
                rating_1     integer
            );
        ''')
        self.connection.commit()

    def close_spider(self, spider):
        # Close the connection
        self.connection.close()

    def process_item(self, item, spider):
        item = ItemAdapter(item)
        # Check if item already exists in the database
        self.cursor.execute("SELECT name FROM app WHERE name = ?", (item['name'],))
        result = self.cursor.fetchone()
        if result:
            print(f"{item['name']} already existed!")
            return item

        # Insert new item into database
        self.cursor.execute('''INSERT INTO app (name, url, image_url, version, last_update, num_download, num_feedback, size, price, kind, category, creator, rating, rating_5, rating_4, rating_3, rating_2, rating_1) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                            (item['name'], item['url'], item['image_url'], item['version'], item.get('last_update'), item.get('num_download'), item.get('num_feedback'), item.get('size'), item.get('price'), item.get('kind'), item.get('category'), item.get('creator'), item.get('rating'), item.get('rating_5'), item.get('rating_4'), item.get('rating_3'), item.get('rating_2'), item.get('rating_1')))
        self.connection.commit()
        return item
