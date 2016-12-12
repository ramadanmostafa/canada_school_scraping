# -*- coding: utf-8 -*-
import scrapy
from ..items import SchoolScrapingItem
from selenium import webdriver
import lxml.html
import time

class TorontoCsdccsSpider(scrapy.Spider):
    """
    a scrapy spider to crawl cspi.qc.ca domain to get
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
    name = "toronto_csdccs"
    allowed_domains = ["csdccs.edu.on.ca"]
    start_urls = (
        "https://www.csdccs.edu.on.ca/ecole/",
    )

    #hit the website slowly not to be detected by captcha defense
    custom_settings = {
        "DOWNLOAD_DELAY" : "30",
        "CONCURRENT_REQUESTS" : "1",
    }

    def parse(self, response):
        """
        parse the start page to get required information about Elementary and Secondary schools listed in the page
        it also use selenium chrome driver to get info from each school page.
        """
        ####################################################################################
        #some useful xpath variables
        schools_names_elementry_xpath = '//*[@id="home"]/div/table/tbody/tr/td[1]/a/span[1]/text()'
        response_urls_elementry_xpath = '//*[@id="home"]/div/table/tbody/tr/td[1]/a/@href'
        cities_elementry_xpath = '//*[@id="home"]/div/table/tbody/tr/td[2]/text()'
        schools_names_secondary_xpath = '//*[@id="profile"]/div/table/tbody/tr/td[1]/a/span[1]/text()'
        response_urls_secondary_xpath = '//*[@id="profile"]/div/table/tbody/tr/td[1]/a/@href'
        cities_secondary_xpath = '//*[@id="profile"]/div/table/tbody/tr/td[2]/text()'
        full_address_xpath = '//address[1]/text()'
        school_url_xpath = '//article/header/h2/a[1]/@href'
        ####################################################################################
        schools_names_elementry = response.xpath(schools_names_elementry_xpath).extract()
        response_urls_elementry = response.xpath(response_urls_elementry_xpath).extract()
        cities_elementry = response.xpath(cities_elementry_xpath).extract()
        index = 0
        for url_elementry in response_urls_elementry:
            #####################################################################
            #init item
            school_item = SchoolScrapingItem()
            school_item["school_name"]	= schools_names_elementry[index]
            school_item['street_address'] = ""
            school_item['city'] = cities_elementry[index]
            school_item['province'] = "Ontario"
            school_item['postal_code'] = ""
            school_item['phone_number'] = ""
            school_item['school_url'] = ""
            school_item['school_grades'] = "Primaire"
            school_item['school_language'] = "French"
            school_item['school_type'] = "Élémentaires"
            school_item['school_board'] = "Conseil scolaire de district catholique Centre-Sud"
            school_item["response_url"] = response.urljoin(url_elementry)
            ###########################################################################################
            driver = webdriver.Chrome()
            driver.get(url_elementry)
            time.sleep(5)
            dom = lxml.html.fromstring(driver.page_source)
            driver.close()
            ##############################################################################
            full_address = map(str.strip, dom.xpath(full_address_xpath))
            full_address = filter(None, full_address)
            school_item['street_address'] = full_address[0]
            school_item['postal_code'] = full_address[1].split(')')[-1]
            school_item['phone_number'] = full_address[2]
            school_item['school_url'] = dom.xpath(school_url_xpath)
            ###########################################################################################
            yield school_item
            #hit the website slowly not to be detected by captcha defense
            time.sleep(30)
            index += 1

        ##############################################################################################
        schools_names_secondary = response.xpath(schools_names_secondary_xpath).extract()
        response_urls_secondary = response.xpath(response_urls_secondary_xpath).extract()
        cities_secondary = response.xpath(cities_secondary_xpath).extract()
        index = 0
        for url_secondary in response_urls_secondary:
            #####################################################################
            #init item
            school_item = SchoolScrapingItem()
            school_item["school_name"]	= schools_names_secondary[index]
            school_item['street_address'] = ""
            school_item['city'] = cities_secondary[index]
            school_item['province'] = "Ontario"
            school_item['postal_code'] = ""
            school_item['phone_number'] = ""
            school_item['school_url'] = ""
            school_item['school_grades'] = "Secondaire"
            school_item['school_language'] = "French"
            school_item['school_type'] = "Secondaire"
            school_item['school_board'] = "Conseil scolaire de district catholique Centre-Sud"
            school_item["response_url"] = response.urljoin(url_secondary)
            ###########################################################################################
            driver = webdriver.Chrome()
            driver.get(url_secondary)
            time.sleep(5)
            dom = lxml.html.fromstring(driver.page_source)
            driver.close()
            ##############################################################################
            full_address = map(str.strip, dom.xpath(full_address_xpath))
            full_address = filter(None, full_address)
            school_item['street_address'] = full_address[0]
            school_item['postal_code'] = full_address[1].split(')')[-1]
            school_item['phone_number'] = full_address[2]
            school_item['school_url'] = dom.xpath(school_url_xpath)
            ###########################################################################################
            yield school_item
            #hit the website slowly not to be detected by captcha defense
            time.sleep(30)
            index += 1
