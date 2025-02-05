from typing import Any
from datetime import date

import jdatetime
import scrapy
from scrapy.http import Response

from miket_scraper.items import MiketItem


class MiketSpider(scrapy.Spider):

    name = "apps"

    start_urls = [
        'https://myket.ir/apps',
        'https://myket.ir/games',
    ]


    def parse(self, response: Response, **kwargs: Any):

        if response.text == '""':
            self.logger.warning(f"Page is empty: {response.url}")
            return

        lists = response.css('.category-list .recommended-header a::attr(href)').getall()
        for list in lists:
            url = 'https://myket.ir' + list
            yield scrapy.Request(url, callback=self.parse_list, errback=self.handle_error)

        categories = response.css('.category-home > a::attr(href)').getall()
        for category in categories:
            url = 'https://myket.ir' + category
            yield scrapy.Request(url, callback=self.parse, errback=self.handle_error)

    def parse_list(self, response: Response, **kwargs: Any):
        if response.text == '""':
            self.logger.warning(f"Page is empty: {response.url}")
            return

        games = response.css(".list-app a")

        for game in games:
            link = 'https://myket.ir' + game.attrib['href']
            name = game.attrib['title']  # or game.xpath("div[@class='appName']/text()").get()
            yield scrapy.Request(link, callback=self.parse_each_game, errback=self.handle_error, cb_kwargs={'name': name})

        # fetching next page
        base_page = response.url.split('page=')[0]
        current_page = 0 if len(response.url.split('page=')) == 1 else int(response.url.split('page=')[-1])
        next_page_url = f"{base_page}&page={current_page + 1}"
        yield scrapy.Request(next_page_url, callback=self.parse, errback=self.handle_error)

    def parse_each_game(self, response: Response, **kwargs: Any):
        name = kwargs['name']
        image_url = response.xpath("//div[@class='appImage']/img/@src").get()
        features_table = response.xpath("//div[@class='tbl-app-detail']/table//td//text()").getall()

        persian_to_english = {
            'نسخه': 'version',
            'آخرین بروزرسانی': 'last_update',
            'تعداد دانلود': 'num_download',
            'امتیاز': 'rating',
            'تعداد نظرات': 'num_feedback',
            'حجم': 'size',
            'نوع': 'kind',
            'دسته‌بندی': 'category',
            'سازنده': 'creator',
            'قیمت': 'price',
        }
        processing_functions = {
            'version': (self.convert_persian_to_english_numbers,),
            'last_update': (self.convert_persian_to_english_numbers, self.convert_jalali_date_to_gregorian),
            'num_download': (self.convert_persian_to_english_numbers, self.convert_persian_words_to_english),
            'rating': (self.convert_persian_to_english_numbers, float),
            'num_feedback': (self.convert_persian_to_english_numbers, lambda val: self.replace_chars(val, {',': ''})),
            'size': (self.convert_persian_to_english_numbers, self.convert_persian_memory_to_bytes),
            'price': (self.convert_persian_to_english_numbers, lambda val: self.replace_chars(val, {',': '', 'تومان': '', 'ریال': ''})),
        }

        features = {}
        for i in range(0, len(features_table), 2):
            persian_key = features_table[i]
            if persian_key in persian_to_english:
                english_key = persian_to_english[persian_key]
                value = features_table[i + 1]

                # Apply processing functions for the given key
                results = value
                for func in processing_functions.get(english_key, []):
                    results = func(results)  # Call the function

                features[english_key] = results
            else:
                with open('non_features.txt', 'a+') as f:
                    f.write(f'url: {response.url} - name: {name} - non feature: {persian_key}\n')

        ratings_percentage = response.xpath("//div[@class='rating-wrapper']//div[@class='progress']/span/@style").getall()
        if ratings_percentage:
            rating_1, rating_2, rating_3, rating_4, rating_5 = (int(rating.split(':')[1].replace('%', '')) for rating in ratings_percentage)
        else:
            rating_1 = rating_2 = rating_3 = rating_4 = rating_5 = None

        item = MiketItem()
        item['name'] = name
        item['url'] = response.url
        item['image_url'] = image_url
        item['rating_1'] = rating_1
        item['rating_2'] = rating_2
        item['rating_3'] = rating_3
        item['rating_4'] = rating_4
        item['rating_5'] = rating_5
        for key, value in features.items():
            item[key] = value
        print(item)

        yield item

    def handle_error(self, failure):
        self.logger.error(repr(failure))
        response = failure.value.response

        if response and response.status == 404:
            self.logger.error(f'Page not found: {response.url}')

    @staticmethod
    def convert_persian_to_english_numbers(persian_str: str) -> str:
        # Mapping of Persian numbers to English numbers
        persian_to_english = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
        return persian_str.translate(persian_to_english)

    @staticmethod
    def convert_jalali_date_to_gregorian(persian_date: str) -> date:
        year, month, day = map(int, persian_date.split('/'))
        jalali_date = jdatetime.date(year, month, day)
        return jalali_date.togregorian()

    @staticmethod
    def convert_persian_words_to_english(persian_str: str) -> int:
        parts = persian_str.split()
        multiplier = 1

        if len(parts) == 2:  # If there are two parts (number + unit)
            number_part = parts[0]
            unit_part = parts[1]

            if 'هزار' in unit_part:
                multiplier = 1000
            elif 'میلیون' in unit_part:
                multiplier = 1_000_000

            num_value = int(number_part) * multiplier
        else:
            # If there's no unit, just convert to English integer
            num_value = int(persian_str)

        return num_value

    @staticmethod
    def convert_persian_memory_to_bytes(persian_str: str) -> int | None:
        unit_values = {
            'بایت': 1,
            'کیلوبایت': 1000,
            'مگابایت': 1000 ** 2,  # 1 Megabyte = 1000 Kilobytes
            'گیگابایت': 1000 ** 3,  # 1 Gigabyte = 1000 Megabytes
            'ترابایت': 1000 ** 4,  # 1 Terabyte = 1000 Gigabytes
        }

        # Split the number and the unit
        parts = persian_str.split()

        if len(parts) == 2:
            number_part = parts[0]
            unit_part = parts[1]

            number_value = float(number_part)
            unit_value = unit_values.get(unit_part)
            if unit_value:
                return int(number_value * unit_value)

        return

    @staticmethod
    def replace_chars(value: str, character_replacements: dict) -> str:
        for old_char, new_char in character_replacements.items():
            value = value.replace(old_char, new_char)
        return value
