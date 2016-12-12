# -*- coding: utf-8 -*-
import scrapy
from ..items import SchoolScrapingItem

class YrdsbSpiderSpider(scrapy.Spider):
    name = "yrdsb_spider"
    allowed_domains = ["yrdsb.ca"]
    start_urls = (
        'http://www.yrdsb.ca/Schools/Pages/default.aspx',
    )

    def parse(self, response):
        """
        extract schools_profiles_urls from the two sections Elementary Schools and Secondary Schools
        """
        #some useful xpath variables
        schools_profiles_urls_xpath1 = '//*[@id="ctl00_PlaceHolderMain_g_8b81db1f_a781_4455_9aa8_7ea4f415c49c_updatePanelctl00_PlaceHolderMain_g_8b81db1f_a781_4455_9aa8_7ea4f415c49c"]/div[2]/div/a/@href'
        schools_profiles_urls_xpath2 = '//*[@id="ctl00_PlaceHolderMain_g_8b81db1f_a781_4455_9aa8_7ea4f415c49d_updatePanelctl00_PlaceHolderMain_g_8b81db1f_a781_4455_9aa8_7ea4f415c49d"]/div[2]/div/a/@href'
        ################################################################################
        schools_profiles_urls1 = response.xpath(schools_profiles_urls_xpath1).extract()
        for url in schools_profiles_urls1:
            yield scrapy.Request(response.urljoin(url), callback=self.parse_school_profile, meta={'school_type':"Elementary School"})
        schools_profiles_urls2 = response.xpath(schools_profiles_urls_xpath2).extract()
        for url in schools_profiles_urls2:
            yield scrapy.Request(response.urljoin(url), callback=self.parse_school_profile, meta={'school_type':"Secondary School"})

    def parse_school_profile(self, response):
        """
        parse school profile page to get all the item data
        """
        #####################################################################
        #init item
        school_item = SchoolScrapingItem()
        school_item["school_name"]	= ""
        school_item['street_address'] = ""
        school_item['city'] = ""
        school_item['province'] = ""
        school_item['postal_code'] = ""
        school_item['phone_number'] = ""
        school_item['school_url'] = ""
        school_item['school_grades'] = ""
        school_item['school_language'] = ""
        school_item['school_type'] = ""
        school_item['school_board'] = ""
        school_item["response_url"] = ""
        ###########################################################################################
        #some useful xpath variables
        xpath_id = 'ctl00_SPWebPartManager1_g_58981a81_8fd7_424c_bdf7_5d05a5eaba49_updatePanelctl00_SPWebPartManager1_g_58981a81_8fd7_424c_bdf7_5d05a5eaba49'
        school_name_xpath = '//*[@id="%s"]/table/tr[1]/td[2]/table/tr[1]/td/text()'
        full_address_xpath = '//*[@id="%s"]/table/tr[1]/td[2]/table/tr[3]/td/text()'
        phone_number_xpath = '//*[@id="%s"]/table/tr[1]/td[2]/table/tr[4]/td[2]/text()'
        school_url_xpath = '//*[@id="%s"]/table/tr[2]/td[2]/table/tr[2]/td/a[1]/@href'
        school_grades_xpath = '//*[@id="%s"]/table/tr[1]/td[2]/table/tr[2]/td/text()'
        ##########################################################################################################
        school_item["school_name"]	= response.xpath(school_name_xpath % xpath_id).extract_first()
        full_address = response.xpath(full_address_xpath % xpath_id).extract()
        school_item['street_address'] = full_address[0]
        school_item['city'] = full_address[1].split(',')[0]
        school_item['province'] = full_address[1].split(',')[1].strip()
        school_item['postal_code'] = full_address[2]
        school_item['phone_number'] = ' '.join(response.xpath(phone_number_xpath % xpath_id).extract())
        school_item['school_url'] = response.xpath(school_url_xpath % xpath_id).extract_first()
        school_item['school_grades'] = response.xpath(school_grades_xpath % xpath_id).extract_first()
        school_item['school_type'] = response.meta['school_type']
        school_item['school_board'] = "York Region District School Board"
        school_item["response_url"] = response.url
        ###########################################################################################
        yield school_item
