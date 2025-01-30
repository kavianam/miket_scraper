from typing import Any

import scrapy


class MiketSpider(scrapy.Spider):

    name = "miket"
    start_urls = [
        "https://myket.ir/list/best-free-android-games"
    ]

    def parse(self, response, **kwargs: Any):
        games = response.xpath("//div[@id='result']//a")

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
