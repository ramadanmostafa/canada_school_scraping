# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SchoolScrapingItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    school_name	= scrapy.Field()
    street_address = scrapy.Field()
    city = scrapy.Field()
    province = scrapy.Field()
    postal_code = scrapy.Field()
    phone_number = scrapy.Field()
    school_url = scrapy.Field()
    school_grades = scrapy.Field()
    school_language = scrapy.Field()
    school_type = scrapy.Field()
    school_board = scrapy.Field()
    response_url = scrapy.Field()
