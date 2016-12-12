# -*- coding: utf-8 -*-
import scrapy
from ..items import SchoolScrapingItem
from selenium import webdriver
import lxml.html

class DpcdsbSpiderSpider(scrapy.Spider):
    name = "dpcdsb_spider"
    allowed_domains = ["dpcdsb.org"]
    start_urls = (
        'http://www3.dpcdsb.org/schools/school-directory',
    )

    def digits_only(self, mystring):
        """
        it takes a sting conains some digits then return the only digits
        """
        result = ""
        for ch in mystring:
            if ch.isdigit() or ch == '-':
                result += ch
        return result

    def parse(self, response):
        """
        parse the page in start_urls tuple which has  all required information
        """
        ###########################################################################################
        #some useful xpath variables
        all_schools_xpath = '//*[@id="schools-directory-result-content"]/div'
        school_name_xpath = '//*[@id="schools-directory-result-content"]/div[%s]/div[2]/div[1]/a/text()'
        address_xpath = '//*[@id="schools-directory-result-content"]/div[%s]/div[2]/div[5]/text()'
        phone_number_xpath = '//*[@id="schools-directory-result-content"]/div[%s]/div[2]/div[6]/text()'
        school_url_xpath = '//*[@id="schools-directory-result-content"]/div[%s]/div[2]/div[1]/a/@href'
        ################################################################################
        #use selenium to get page source because some javascript need to be executed
        driver = webdriver.Chrome()
        driver.get(response.url)
        dom = lxml.html.fromstring(driver.page_source)
        driver.close()
        ##############################################################################
        for i in range(len(dom.xpath(all_schools_xpath))):
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
            school_item['school_board'] = "Dufferin-Peel Catholic District School Board"
            school_item["response_url"] = response.url
            ##########################################################################################################
            address = dom.xpath(address_xpath % str(i + 1))
            school_item["school_name"]	= dom.xpath(school_name_xpath % str(i + 1))[0].strip()
            school_item['street_address'] = address[0].strip()
            school_item['city'] = address[1].split(',')[0].strip()
            school_item['province'] = address[1].split(',')[1].strip()
            school_item['postal_code'] = address[2].strip()
            school_item['phone_number'] = self.digits_only(dom.xpath(phone_number_xpath % str(i + 1))[0]).strip()
            school_item['school_url'] = dom.xpath(school_url_xpath % str(i + 1))[0].strip()
            yield school_item
