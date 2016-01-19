#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import ast
import scrapy
from olx_spider.items import OlxSpiderItem

class OlxSpider(scrapy.Spider):
    name = "olx"
    allowed_domains = ["olx.kz",]
    start_urls = [
        "http://olx.kz/"
    ]

    def parse(self, response):
        for category_url in response.css(".maincategories .subcategories-list > ul > li > a::attr('href')"):
            yield scrapy.Request(category_url.extract(), callback=self.parse_category_follow_next_page)

    def parse_category_follow_next_page(self, response):
        for item_url in response.css(".offer .detailsLink::attr('href')"):
            yield scrapy.Request(item_url.extract(), callback=self.parse_item)

        next_page = response.css(".pager .next > a::attr('href')").extract_first()
        if next_page:
          yield scrapy.Request(next_page, callback=self.parse_category_follow_next_page)

    def parse_item(self, response):
        item = OlxSpiderItem()
        item['url'] = response.url
        item['city'] = response.css(".offerheadinner .show-map-link").xpath("strong/text()").extract_first()
        item['name'] = response.css("#offerbox .userdetails").xpath("span/text()").extract_first()

        phones_tag = response.css("#contact_methods > li").extract_first() or None
        try:
            phones_id = phones_tag.split("id':'")[1].split("'")[0]
        except:
            phones_id = None
        else:
            phones_url = u"http://olx.kz/ajax/misc/contact/phone/%s/"%phones_id
            request = scrapy.Request(phones_url,  callback = self.get_phones)
            request.meta['item'] = item
            yield request

        item['longitude'] = response.css("#mapcontainer::attr('data-lon')").extract()
        item['latitude'] = response.css("#mapcontainer::attr('data-lat')").extract()
        item['radius'] = response.css("#mapcontainer::attr('data-rad')").extract()

        for desc_item in response.css(".descriptioncontent .item"):
            if desc_item.css("tbody > tr").xpath('th/text()').extract_first() == u"Объявление от":
                item['offerer_type'] = desc_item.css(".value").xpath("a/text()").extract_first()

    def get_phones(self, response):
        phones = ast.literal_eval(response.body)['value']
        phones_list = re.findall("[0-9]+", phones.replace(" ", ""))
        response.meta['item']['phones'] = phones_list
        return response.meta['item']
