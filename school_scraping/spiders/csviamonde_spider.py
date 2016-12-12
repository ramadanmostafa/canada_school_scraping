# -*- coding: utf-8 -*-
import scrapy
from ..items import SchoolScrapingItem
from selenium import webdriver
import lxml.html
import time

class CsviamondeSpiderSpider(scrapy.Spider):
    """
    a scrapy spider to crawl csviamonde.ca domain to get
    school_name
    street_address
    city
    province
    postal_code
    phone_number
    school_url
    school_grades
    school_language
    school_type
    school_board
    response_url
    for each school found
    """
    name = "csviamonde_spider"
    allowed_domains = ["csviamonde.ca"]
    start_urls = (
        'http://csviamonde.ca/nosecoles/Pages/default.aspx',
    )

    def parse(self, response):
        """
        extract schools_profiles_urls from the two sections Elementary Schools and Secondary Schools
        """
        #some useful xpath variables
        schools_profiles_urls_xpath1 = '//*[@id="FindSchoolContainer"]/div[5]/div[3]/div[2]/div/div/a/@href'
        schools_profiles_urls_xpath2 = '//*[@id="FindSchoolContainer"]/div[5]/div[6]/div[2]/div/div/a/@href'
        ################################################################################
        driver = webdriver.Chrome()
        driver.get(response.url)
        time.sleep(5)
        dom = lxml.html.fromstring(driver.page_source)
        driver.close()
        ##############################################################################
        schools_profiles_urls1 = dom.xpath(schools_profiles_urls_xpath1)
        schools_profiles_urls2 = dom.xpath(schools_profiles_urls_xpath2)
        ##############################################################################
        for url in schools_profiles_urls1:
            yield scrapy.Request(response.urljoin(url), callback=self.parse_school_profile, meta={'school_type':"Elementary"})
        for url in schools_profiles_urls2:
            yield scrapy.Request(response.urljoin(url), callback=self.parse_school_profile, meta={'school_type':"Secondary"})

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
        school_item['school_grades'] = response.meta['school_type']
        school_item['school_language'] = ""
        school_item['school_type'] = ""
        school_item['school_board'] = ""
        school_item["response_url"] = ""
        ###########################################################################################
        #some useful xpath variables
        school_name_xpath = '//*[@id="GroupDetails"]/div[1]/text()'
        school_url_xpath = '//*[@id="FSDInfodetailsTab1"]/div[2]/div[1]/div[4]/div[2]/a/@href'
        ##########################################################################################################
        details = map(unicode.strip, response.xpath('//*[@id="FSDInfodetailsTab1"]/div[2]/div[1]/div/div/text()').extract())
        address_index = details.index('Adresse :')
        school_item["school_name"]	= response.xpath(school_name_xpath).extract_first()
        school_item['street_address'] = details[address_index + 1]
        school_item['city'] = details[address_index + 3].split(',')[0]
        school_item['province'] = details[address_index + 3].split(',')[1]
        school_item['postal_code'] = details[address_index + 5]
        school_item['phone_number'] = details[1]
        school_item['school_url'] = response.xpath(school_url_xpath).extract_first()
        school_item['school_language'] = "French"
        school_item['school_type'] = response.meta['school_type']
        school_item['school_board'] = "Conseil scolaire Viamonde"
        school_item["response_url"] = response.url
        ###########################################################################################
        yield school_item
