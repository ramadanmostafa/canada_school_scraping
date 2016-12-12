# -*- coding: utf-8 -*-
import scrapy
from ..items import SchoolScrapingItem


class HcdsbSpiderSpider(scrapy.Spider):
    name = "hcdsb_spider"
    allowed_domains = ["hcdsb.org"]
    start_urls = (
        'http://www.hcdsb.org/Schools/Profiles/Pages/index.aspx',
    )

    def parse(self, response):
        ###########################################################################################
        #some useful xpath variables
        schools_profiles_urls_xpath = '//*[@id="WebPartWPQ3"]/table/tr/td[1]/a/@href'
        ##################################################################################
        schools_profiles_urls = response.xpath(schools_profiles_urls_xpath).extract()
        for url in schools_profiles_urls:
            yield scrapy.Request(response.urljoin(url), callback=self.parse_school_profile)

    def parse_school_profile(self, response):
        ###########################################################################################
        #some useful xpath variables
        school_data_xpath = '//*[@id="WebPartWPQ5"]/table/tr/td/table/tr/td/text()'
        school_name_xpath = '//*[@id="WebPartWPQ5"]/table/tr/td/table/tr/td/h4/text()'
        school_url_xpath = '//*[@id="WebPartWPQ5"]/table/tr/td/table/tr/td/a[2]/@href'
        ##################################################################################
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
        school_item['school_board'] = "Halton Catholic District School Board"
        school_item["response_url"] = response.url
        ##########################################################################################################
        school_data = response.xpath(school_data_xpath).extract()
        school_item["school_name"]	= response.xpath(school_name_xpath).extract_first()
        school_item['street_address'] = school_data[0]
        school_item['city'] = school_data[1].split(',')[0]
        school_item['province'] = school_data[1].split(',')[1]
        school_item['postal_code'] = school_data[1].split(',')[2]
        school_item['phone_number'] = school_data[2].split()[1]
        school_item['school_url'] = response.xpath(school_url_xpath).extract_first()
        school_item['school_grades'] = ""
        school_item['school_language'] = ""
        if school_item["school_name"].split()[-2] == "Elementary":
            school_item['school_type'] = "Elementary School"
            school_item['school_grades'] = "Elementary"
        elif school_item["school_name"].split()[-2] == "Secondary":
            school_item['school_type'] = "Secondary School"
            school_item['school_grades'] = "Secondary"


        yield school_item
