#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy

class SpiderItem(scrapy.Item):
    url = scrapy.Field()
    phones = scrapy.Field() 
    city = scrapy.Field()
    name = scrapy.Field()
    offerer_type = scrapy.Field()
    longitude = scrapy.Field()
    latitude = scrapy.Field()
    radius = scrapy.Field()