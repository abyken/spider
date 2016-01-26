#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import re
import ast
import scrapy
from olx_spider.items import SpiderItem

URL = u"http://kolesa.kz"
URL_PATTERN = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
class KolesaSpider(scrapy.Spider):
    name = "kolesa"
    allowed_domains = ["kolesa.kz",]
    start_urls = [
        "http://kolesa.kz/"
    ]

    def parse(self, response):
        for _category in response.css("#nav-main-center > ul > li > a::attr('href')"):
            category = _category.extract()
            if not "content" in category:
                yield scrapy.Request(category, callback=self.parse_category)

    def parse_category(self, response):
        for region in response.css(".cities-block .clearfix > ul > li > a::attr('href')"):
            region_url = region.extract()
            if re.match(URL_PATTERN, region_url):
                yield scrapy.Request(region_url, callback=self.parse_region_follow_next_page)
            else:
                yield scrapy.Request(URL+region_url, callback=self.parse_region_follow_next_page)


    def parse_region_follow_next_page(self, response):
        for item in response.css(".good .photo > a::attr('href')"):
            item_url = URL+item.extract()
            yield scrapy.Request(item_url, callback=self.parse_item)

        # next_page = response.css(".next_page::attr('href')").extract_first()
        # if next_page:
        #   yield scrapy.Request(next_page, callback=self.parse_region_follow_next_page)

    def parse_item(self, response):
        item = SpiderItem()
        item['url'] = response.url
        item['city'] = response.css(".description-body .clearfix").xpath("dd/text()").extract_first()
        print item
        phones_tag = response.css(".phones-box .showPhonesLink::attr('data-href')").extract_first() or None
        if phones_tag:
            phones_url = URL+phones_tag
            request = scrapy.Request(phones_url,  callback = self.get_phones)
            request.meta['item'] = item
            yield request

    def get_phones(self, response):
        phones = response.body
        phones_list = re.findall("[0-9]+", phones)
        response.meta['item']['phones'] = phones_list
        return response.meta['item']