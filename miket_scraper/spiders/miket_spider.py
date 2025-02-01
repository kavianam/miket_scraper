from typing import Any
from datetime import date

import jdatetime
import scrapy
from scrapy.http import Response

from miket_scraper.items import MiketItem


class MiketSpider(scrapy.Spider):

    name = "miket"

    pages = (
        'best-free-android-games',
        'most-popular-iranian-android-games',
        'best-online-games-for-android',
        'best-offline-games-for-android',
        'best-strategy-games-for-android',
        'best-android-puzzle-games',
        'best-android-card-battle-games'
    )
    base_url = "https://myket.ir/list/applicationPackage/page"
    start_urls = [f'https://myket.ir/list/page?listKey={page}&page=0' for page in pages]


    def parse(self, response: Response, **kwargs: Any):

        if response.text == '""':
            self.logger.warning(f"Page is empty: {response.url}")
            return

        print('=' * 50)
        print(f"Scraping: {response.url}")
        games = response.css(".list-app a")

        for game in games:
            link = 'https://myket.ir' + game.attrib['href']
            name = game.attrib['title']  # or game.xpath("div[@class='appName']/text()").get()
            title_fa = game.xpath("p[@class='app-group']//text()").get()  # not all have - it is a category
            image_url = game.xpath('img/@src').get()
            print(f'{link=}')
            print(f'{name=}')
            print(f'{title_fa=}')
            print(f'{image_url=}')
            print('-' * 50)
            yield scrapy.Request(link, callback=self.parse_each_game, errback=self.handle_error, cb_kwargs={'name': name})

        # fetching next page
        base_page = response.url.split('page=')[0]
        current_page = int(response.url.split('page=')[-1])
        next_page_url = f"{base_page}&page={current_page + 1}"
        yield scrapy.Request(next_page_url, callback=self.parse, errback=self.handle_error)

    def handle_error(self, failure):
        self.logger.error(repr(failure))
        response = failure.value.response

        if response and response.status == 404:
            self.logger.error(f'Page not found: {response.url}')


    def parse_each_game(self, response: Response, **kwargs: Any):
        name = kwargs['name']
        # name = response.css('section.topApp-section.first-section h1::text').get()
        # name_fa, name = map(str.strip, name.split('-'))

        image_url = response.xpath("//div[@class='appImage']/img/@src").get()

        print(f'{image_url=}')
        print(f'{name=}')

        features_table = response.xpath("//div[@class='tbl-app-detail']/table//td//text()").getall()
        features_value = [text for index, text in enumerate(features_table) if index % 2 != 0]
        print(features_value)

        version = self.convert_persian_to_english_numbers(features_value[0])
        last_update = self.convert_jalali_date_to_gregorian(self.convert_persian_to_english_numbers(features_value[1]))
        num_download = self.convert_persian_words_to_english(self.convert_persian_to_english_numbers(features_value[2]))
        rating = float(self.convert_persian_to_english_numbers(features_value[3]))
        num_feedback = int(self.convert_persian_to_english_numbers(features_value[4]).replace(',', ''))
        size = self.convert_persian_memory_to_bytes(self.convert_persian_to_english_numbers(features_value[5]))
        kind = features_value[6].strip()
        category = features_value[7].strip()
        creator = features_value[8].strip()

        print(f'{version=}')
        print(f'{last_update=}')
        print(f'{num_download=}')
        print(f'{rating=}')
        print(f'{num_feedback=}')
        print(f'{size=}')
        print(f'{kind=}')
        print(f'{category=}')
        print(f'{creator=}')

        # ratings:
        ratings_percentage = response.xpath("//div[@class='rating-wrapper']//div[@class='progress']/span/@style").getall()
        print(ratings_percentage)
        ratings_percentage = [int(rating.split(':')[1].replace('%', '')) for rating in ratings_percentage]
        print(f'{ratings_percentage=}')
        print('=' * 50)

        item = MiketItem()
        item['name'] = name
        item['image_url'] = image_url
        item['version'] = version
        item['last_update'] = last_update
        item['num_download'] = num_download
        item['rating'] = rating
        item['num_feedback'] = num_feedback
        item['size'] = size
        item['kind'] = kind
        item['category'] = category
        item['creator'] = creator
        item['ratings_percentage'] = ratings_percentage
        print(item)

        yield item


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
