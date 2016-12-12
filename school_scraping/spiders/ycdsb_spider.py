# -*- coding: utf-8 -*-
import scrapy
from ..items import SchoolScrapingItem


class YcdsbSpiderSpider(scrapy.Spider):
    name = "ycdsb_spider"
    allowed_domains = ["ycdsb.ca"]
    start_urls = (
        'http://www.ycdsb.ca/schools/default.htm',
    )

    def parse(self, response):
        ###########################################################################################
        #some useful xpath variables
        num_elementry_xpath = '//*[@id="elementary"]/div'
        num_secondary_xpath = '//*[@id="secondary"]/div'
        num_alternative_xpath = '//*[@id="tab-3"]/div'
        address_xpath1 = '//*[@id="elementary"]/div[%s]/div[2]/p/a/text()'
        address_xpath2 = '//*[@id="secondary"]/div[%s]/div[2]/p/a/text()'
        address_xpath3 = '//*[@id="tab-3"]/div[%s]/div[2]/p/text()'
        school_name_xpath1 = '//*[@id="elementary"]/div[%s]/div[2]/h3/text()'
        school_name_xpath2 = '//*[@id="secondary"]/div[%s]/div[2]/h3/text()'
        school_name_xpath3 = '//*[@id="tab-3"]/div[%s]/div[2]/h3/text()'
        phone_number_xpath1 = '//*[@id="elementary"]/div[%s]/div[2]/p[2]/text()'
        phone_number_xpath2 = '//*[@id="secondary"]/div[%s]/div[2]/p[2]/text()'
        phone_number_xpath3 = '//*[@id="tab-3"]/div[%s]/div[2]/p[2]/text()'
        school_url_xpath1 = '//*[@id="elementary"]/div[%s]/div[3]/ul/li/a/@href'
        school_url_xpath2 = '//*[@id="secondary"]/div[%s]/div[3]/ul/li/a/@href'
        school_url_xpath3 = '//*[@id="tab-3"]/div[%s]/div[3]/ul/li/a/@href'
        ############################################################################################
        num_elementry = len(response.xpath(num_elementry_xpath).extract())
        for i in range(num_elementry):
            #####################################################################
            #init item
            school_item = SchoolScrapingItem()
            school_item["school_name"]	= ''
            school_item['street_address'] = ''
            school_item['city'] = ""
            school_item['province'] = ""
            school_item['postal_code'] = ""
            school_item['phone_number'] = ""
            school_item['school_url'] = ""
            school_item['school_grades'] = ""
            school_item['school_language'] = "English"
            school_item['school_type'] = ""
            school_item['school_board'] = "York Catholic District School Board"
            school_item["response_url"] = response.url
            ##########################################################################################################
            address =  response.xpath(address_xpath1 % str(i + 1)).extract_first().split(',')
            if len(address) > 2:
                address = [address[0], ' '.join(address[1:])]
            school_item["school_name"]	= response.xpath(school_name_xpath1 % str(i + 1)).extract_first()
            school_item['street_address'] = address[0]
            school_item['city'] = address[1].split()[0]
            school_item['province'] = "ON"
            school_item['postal_code'] = ' '.join(address[1].split()[1:])
            if len(address[1].split()) > 3:
                school_item['city'] = ' '.join(address[1].split()[0:2])
                school_item['postal_code'] = ' '.join(address[1].split()[2:])
            school_item['phone_number'] = response.xpath(phone_number_xpath1 % str(i + 1)).extract_first().split()[1]
            school_item['school_url'] = response.xpath(school_url_xpath1 % str(i + 1)).extract()[-1]
            school_item['school_grades'] = "Elementry"
            school_item['school_language'] = ""
            school_item['school_type'] = "Elementry"
            yield school_item
        #######################################################
        num_secondary = len(response.xpath(num_secondary_xpath).extract())
        for i in range(num_secondary):
            #####################################################################
            #init item
            school_item = SchoolScrapingItem()
            school_item["school_name"]	= ''
            school_item['street_address'] = ''
            school_item['city'] = ""
            school_item['province'] = ""
            school_item['postal_code'] = ""
            school_item['phone_number'] = ""
            school_item['school_url'] = ""
            school_item['school_grades'] = ""
            school_item['school_language'] = ""
            school_item['school_type'] = ""
            school_item['school_board'] = "York Catholic District School Board"
            school_item["response_url"] = response.url
            ##########################################################################################################
            address =  response.xpath(address_xpath2 % str(i + 1)).extract_first().split(',')
            school_item["school_name"]	= response.xpath(school_name_xpath2 % str(i + 1)).extract_first()
            school_item['street_address'] = address[0]
            school_item['city'] = address[1].split()[0]
            school_item['province'] = "ON"
            school_item['postal_code'] = ' '.join(address[1].split()[1:])
            if len(address[1].split()) > 3:
                school_item['city'] = ' '.join(address[1].split()[0:2])
                school_item['postal_code'] = ' '.join(address[1].split()[2:])
            school_item['phone_number'] = response.xpath(phone_number_xpath2 % str(i + 1)).extract_first().split()[1]
            school_item['school_url'] = response.xpath(school_url_xpath2 % str(i + 1)).extract()[-1]
            school_item['school_grades'] = "Secondary"
            school_item['school_language'] = "English"
            school_item['school_type'] = "Secondary"
            yield school_item
        #######################################################
        num_alternative = len(response.xpath(num_alternative_xpath).extract())
        for i in range(num_alternative):
            #####################################################################
            #init item
            school_item = SchoolScrapingItem()
            school_item["school_name"]	= ''
            school_item['street_address'] = ''
            school_item['city'] = ""
            school_item['province'] = ""
            school_item['postal_code'] = ""
            school_item['phone_number'] = ""
            school_item['school_url'] = ""
            school_item['school_grades'] = ""
            school_item['school_language'] = ""
            school_item['school_type'] = ""
            school_item['school_board'] = "York Catholic District School Board"
            school_item["response_url"] = response.url
            ##########################################################################################################
            address =  response.xpath(address_xpath3 % str(i + 1)).extract_first().split(',')#
            school_item["school_name"]	= response.xpath(school_name_xpath3 % str(i + 1)).extract_first()
            school_item['street_address'] = address[0]
            school_item['city'] = address[1].split()[0]
            school_item['province'] = "ON"
            school_item['postal_code'] = ' '.join(address[1].split()[1:])
            if len(address[1].split()) > 3:
                school_item['city'] = ' '.join(address[1].split()[0:2])
                school_item['postal_code'] = ' '.join(address[1].split()[2:])
            school_item['phone_number'] = response.xpath(phone_number_xpath3 % str(i + 1)).extract_first().split()[1]
            school_item['school_url'] = response.xpath(school_url_xpath3 % str(i + 1)).extract()[-1]
            school_item['school_grades'] = ""
            school_item['school_language'] = "English"
            school_item['school_type'] = "alternative"
            yield school_item
