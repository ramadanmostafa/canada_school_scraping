# -*- coding: utf-8 -*-
import scrapy
from ..items import SchoolScrapingItem
from selenium import webdriver
import lxml.html


class HdsbSpiderSpider(scrapy.Spider):
    name = "hdsb_spider"
    allowed_domains = ["hdsb.ca"]
    handle_httpstatus_list = [302]
    start_urls = (
        'https://www.hdsb.ca/schools/Pages/Find%20My%20Local%20School/School-Listing.aspx',
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
        ###########################################################################################
        #some useful xpath variables
        schools_details_urls_xpath = '//tr/td[4]/a/@href'
        ################################################################################
        #use selenium to get page source because some javascript need to be executed
        driver = webdriver.Chrome()
        driver.get(response.url)
        dom = lxml.html.fromstring(driver.page_source)
        driver.close()
        ##############################################################################
        schools_details_urls = dom.xpath(schools_details_urls_xpath)
        for url in schools_details_urls:
            yield scrapy.Request(response.urljoin(url), callback=self.parse_detail)

    def parse_detail(self, response):
        if response.status == 302:
            yield scrapy.Request(response.headers["Location"], callback=self.parse_detail)
        else:
            ###########################################################################################
            #some useful xpath variables
            address_phone_xpath = '//div/div[1]/table/tr/td[1]/div/text()'
            school_name_xpath = '//*[@id="ctl00_MainContent_hlkSchool"]/text()'
            school_url_xpath = '//*[@id="ctl00_MainContent_hlkSchool"]/@href'
            school_grades_xpath = '//div/div/table/tr/td/div/div/table/tr/td/text()'
            ####################################################################
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
            school_item['school_board'] = "Halton District School Board"
            school_item["response_url"] = response.url
            ##########################################################################################################
            address_phone = filter(None, map(unicode.strip, response.xpath(address_phone_xpath).extract()))
            school_item["school_name"]	= response.xpath(school_name_xpath).extract_first()
            school_item['street_address'] = address_phone[0]
            school_item['city'] = address_phone[1].split(',')[0]
            school_item['province'] = "ON"
            school_item['postal_code'] = address_phone[1].split(',')[1]
            school_item['phone_number'] = self.digits_only(address_phone[2])
            school_item['school_url'] = response.xpath(school_url_xpath).extract_first()
            school_item['school_grades'] = response.xpath(school_grades_xpath).extract()[1].strip()
            school_item['school_type'] = ' '.join(school_item["school_name"].split()[-2:])
            yield school_item
