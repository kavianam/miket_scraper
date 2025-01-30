from typing import Any

import scrapy


class MiketSpider(scrapy.Spider):

    name = "miket"

    start_urls = [
        "https://myket.ir/list/applicationPackage/page?listKey=best-free-android-games&page=0"
    ]

    def parse(self, response, **kwargs: Any):

        if response.text == '""':
            self.logger.warning(f"Page is empty: {response.url}")
            return

        print('=' * 50)
        print(f"Scraping: {response.url}")
        games = response.css(".listApps a")

        for game in games:
            link = game.attrib['href']
            title = game.attrib['title']  # or game.xpath("div[@class='appName']/text()").get()
            title_fa = game.xpath("div[@class='appGroup']//text()").get()
            image_url = game.xpath('picture/source').attrib['srcset']
            print(f'{link=}')
            print(f'{title=}')
            print(f'{title_fa=}')
            print(f'{image_url=}')
            print('-' * 50)

        current_page = int(response.url.split('page=')[-1])
        next_page = current_page + 1
        next_page_url = f"https://myket.ir/list/applicationPackage/page?listKey=best-free-android-games&page={next_page}"
        yield scrapy.Request(next_page_url, callback=self.parse, errback=self.handle_error)

    def handle_error(self, failure):
        self.logger.error(repr(failure))
        response = failure.value.response

        if response and response.status == 404:
            self.logger.error(f'Page not found: {response.url}')
