# -*- coding: utf-8 -*-
import scrapy
from ..items import SchoolScrapingItem
from selenium import webdriver
import lxml.html
import time

class TdsbSpiderSpider(scrapy.Spider):
    """
    scrapy spider to crawl tdsb.on.ca domain
    you can run it using something like that
    scrapy crawl tdsb_spider
    it also uses selenium Chrome webdriver so make sure it's installed.
    """
    name = "tdsb_spider"
    allowed_domains = ["tdsb.on.ca"]
    start_urls = (
        'http://www.tdsb.on.ca/',
    )

    def parse(self, response):
        """
        parse the home page to get the url of the search page
        """
        ###############################################################
        search_url_xpath = '//*[@id="TDSBpageFrameHome"]/div[1]/div[2]/div[1]/a[1]/@href'
        ###############################################################
        search_url = response.xpath(search_url_xpath).extract_first()
        yield scrapy.Request(response.urljoin(search_url), callback = self.parse_search_page)

    def parse_search_page(self, response):
        """
        parse the search page to get a link to search by name page
        """
        ###############################################################
        search_name_url_xpath = '//*[@id="dnn_dnnLEFTMENU_RadPanel1"]/ul/li/div/ul/li[2]/a/@href'
        ###############################################################
        search_name_url = response.xpath(search_name_url_xpath).extract_first()
        yield scrapy.Request(response.urljoin(search_name_url), callback = self.parse_search_name_page)

    def parse_search_name_page(self, response):
        """
        use selenium to click on each letter, wait some seconds to make sure the javascript script is done.
        then build a list containing links to all school pages
        """
        ###############################################################
        schools_pages_url_xpath = '//*[@id="SchoolSearchResults"]/li/a/@href'
        letter_id = "dnn_ctr1658_SchoolSearch_rptLetterNav_lnkLetter_%s"
        ###############################################################
        schools_pages_url = []
        for i in range(26):
            driver = webdriver.Chrome()
            driver.get(response.url)
            driver.find_element_by_id(letter_id % str(i)).click()
            time.sleep(10)
            dom = lxml.html.fromstring(driver.page_source)
            driver.close()
            schools_pages_url += dom.xpath(schools_pages_url_xpath)

        for url in schools_pages_url:
            yield scrapy.Request(response.urljoin(url), callback = self.parse_school_page)

    def parse_school_page(self, response):
        """
        parse the school page to get required information and yield the item to the pipeline
        """
        #############################################################################################
        #some useful xpath variables
        school_name_xpath = '//*[@id="dnn_ctr2796_ViewSPC_ctl00_lblSchoolName"]/text()'
        street_address_xpath = '//*[@id="dnn_ctr2796_ViewSPC_ctl00_lblAddress"]/text()'
        city_xpath = '//*[@id="dnn_ctr2796_ViewSPC_ctl00_lblAddress"]/text()'
        province_xpath = '//*[@id="dnn_ctr2796_ViewSPC_ctl00_lblAddress"]/text()'
        postal_code_xpath = '//*[@id="dnn_ctr2796_ViewSPC_ctl00_lblAddress"]/text()'
        phone_number_xpath = '//*[@id="dnn_ctr2796_ViewSPC_ctl00_lblPhone"]/text()'
        school_url_xpath = '//*[@id="dnn_ctr2796_ViewSPC_ctl00_hplViewWebsite"]/@href'
        school_grades_xpath = '//*[@id="dnn_ctr2796_ViewSPC_ctl00_lblGrades"]/text()'
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
        school_item["school_name"]	= response.xpath(school_name_xpath).extract_first()
        school_item['street_address'] = response.xpath(street_address_xpath).extract()[0].split(',')[0]
        school_item['city'] = response.xpath(city_xpath).extract()[0].split(',')[-2]
        school_item['province'] = response.xpath(province_xpath).extract()[0].split(',')[-1]
        school_item['postal_code'] = response.xpath(postal_code_xpath).extract()[1]
        school_item['phone_number'] = response.xpath(phone_number_xpath).extract_first()
        school_item['school_url'] = response.xpath(school_url_xpath).extract_first()
        school_item['school_grades'] = response.xpath(school_grades_xpath).extract_first()
        school_item['school_board'] = "Toronto District School Board"
        school_item["response_url"] = response.url

        yield school_item
