import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from bankcomm.items import Article


class bankcommSpider(scrapy.Spider):
    name = 'bankcomm'
    start_urls = ['http://www.bankcomm.com/BankCommSite/shtml/jyjr/cn/7158/7162/list_1.shtml?channelId=7158']
    page = 1

    def parse(self, response):
        articles = response.xpath('//ul[@class="tzzgx-conter ty-list"]/li')
        if articles:
            for article in articles:
                link = article.xpath('./a/@href').get()
                date = article.xpath('./a/span/text()').get()
                if date:
                    date = " ".join(date.split())

                yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

            self.page += 1
            next_page = f'http://www.bankcomm.com/BankCommSite/shtml/jyjr/cn/7158/7162/' \
                        f'list_{self.page}.shtml?channelId=7158'
            yield response.follow(next_page, self.parse)

    def parse_article(self, response, date):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h2/text()').get()
        if title:
            title = title.strip()
        else:
            return

        content = response.xpath('//div[@class="show_main c_content"]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content[:-1]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
