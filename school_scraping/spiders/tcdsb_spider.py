# -*- coding: utf-8 -*-
import scrapy
from ..items import SchoolScrapingItem

class TcdsbSpiderSpider(scrapy.Spider):
    """
    scrapy spider to crawl tcdsb.org domain
    you can run it using something like that
    scrapy crawl tcdsb_spider
    """
    name = "tcdsb_spider"
    allowed_domains = ["tcdsb.org"]
    handle_httpstatus_list = [302]
    start_urls = (
        'https://www.tcdsb.org/',
    )
    def parse(self, response):
        """
        parse the home page to get the url of the search page
        """
        schools_page_url_xpath = '//*[@id="main-nav"]/div/ul/li[3]/a/@href'
        if response.status == 302:
            yield scrapy.Request(response.headers["Location"], callback=self.parse)
        else:
            schools_page_url = response.urljoin(response.xpath(schools_page_url_xpath).extract_first())
            yield scrapy.Request(schools_page_url, callback=self.parse_schools_page)

    def parse_schools_page(self, response):
        """
        parse the search page to get the url of the alohabetic directory page
        """
        alphabetic_dir_url_xpath = '//*[@id="main"]/div/div/aside/nav/ul/li[1]/div/ul/li[2]/a/@href'
        alphabetic_dir_url = response.urljoin(response.xpath(alphabetic_dir_url_xpath).extract_first())
        yield scrapy.Request(alphabetic_dir_url, callback=self.parse_alphabetic_dir)

    def parse_alphabetic_dir(self, response):
        """
        the alohabetic directory page contains all required information for all schools,
        so parse it and yield the item to the pipeline routine.
        """
        ###########################################################################################################
        schools_num_xpath = '//*[@id="ctl00_ctl21_g_5b737a68_affa_412e_8609_12afea344476_ctl00"]/tr/td[2]/a'
        school_name_xpath = '//*[@id="ctl00_ctl21_g_5b737a68_affa_412e_8609_12afea344476_ctl00"]/tr[%s]/td[2]/a/text()'
        school_address_xpath = '//*[@id="ctl00_ctl21_g_5b737a68_affa_412e_8609_12afea344476_ctl00"]/tr[%s]/td[4]/text()'
        phone_number_xpath = '//*[@id="ctl00_ctl21_g_5b737a68_affa_412e_8609_12afea344476_ctl00"]/tr[%s]/td[7]/text()'
        school_url_xpath = '//*[@id="ctl00_ctl21_g_5b737a68_affa_412e_8609_12afea344476_ctl00"]/tr[%s]/td[2]/a/@href'
        school_type_xpath = '//*[@id="ctl00_ctl21_g_5b737a68_affa_412e_8609_12afea344476_ctl00"]/tr[%s]/td[3]/text()'
        ###############################################################################################################
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
        #####################################################################
        schools_num = len(response.xpath(schools_num_xpath).extract())
        for i in range(2, schools_num + 2):
            school_item["school_name"]	= response.xpath(school_name_xpath % str(i)).extract_first()
            school_address = response.xpath(school_address_xpath % str(i)).extract_first()
            school_item['street_address'] = ' '.join(school_address.split()[:school_address.split().index("ON")-1])
            school_item['city'] = school_address.split()[-4]
            school_item['province'] = school_address.split()[-3]
            school_item['postal_code'] = ' '.join(school_address.split()[-2:])
            school_item['phone_number'] = response.xpath(phone_number_xpath % str(i)).extract_first()
            school_item['school_url'] = response.xpath(school_url_xpath % str(i)).extract_first()
            school_item['school_type'] = response.xpath(school_type_xpath % str(i)).extract_first()
            school_item['school_grades'] = school_item['school_type']
            school_item['school_board'] = "Toronto Catholic District School Board"
            school_item["response_url"] = response.url
            if school_item['province'] != 'ON':
                school_item['city'] = school_address.split()[-3]
                school_item['province'] = school_address.split()[-2]
                school_item['postal_code'] = school_address.split()[-1]
            yield school_item
