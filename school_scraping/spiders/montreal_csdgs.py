# -*- coding: utf-8 -*-
import scrapy
from ..items import SchoolScrapingItem
from selenium import webdriver
import lxml.html
import time

class MontrealCsdgsSpider(scrapy.Spider):
    """
    a scrapy spider to crawl csdgs.qc.ca domain to get
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
    name = "montreal_csdgs"
    allowed_domains = ["csdgs.qc.ca"]
    start_urls = (
        "http://www.csdgs.qc.ca/ecoles-centres-et-programmes/carte-des-etablissements/?filter=0&program_id=0&city=0&loade_carte=1",
    )

    def parse(self, response):
        """
        this method uses selenium to get data from the start page. it Requests the page then wait for 10 secs to
        make sure the JS script is done then store the page source into dom variable
        then it uses dom to extract required data.
        """
        ###########################################################################################################
        #some useful xpath variables
        num_schools_xpath = '//*[@id="wpsl-stores"]/ul/li'
        school_name_xpath = '//*[@id="wpsl-stores"]/ul/li[%s]/div[1]/p/strong/text()'
        street_address_xpath = '//*[@id="wpsl-stores"]/ul/li[%s]/div[1]/p/span[1]/text()'
        data_city_postcode_xpath = '//*[@id="wpsl-stores"]/ul/li[%s]/div[1]/p/span[2]/text()'
        phone_number_xpath = '//*[@id="wpsl-stores"]/ul/li[%s]/div[1]/div[1]/p/span[1]/text()'
        school_url_xpath = '//*[@id="wpsl-stores"]/ul/li[%s]/div[1]/div[1]/p/span/a/@href'
        #######################################################################################
        #selenium section begins
        driver = webdriver.Chrome()
        driver.get(response.url)
        time.sleep(10)
        dom = lxml.html.fromstring(driver.page_source)
        driver.close()
        ##########################################################################################
        #for each school item in the page
        num_schools = len(dom.xpath(num_schools_xpath))
        for index in range(num_schools):
            #####################################################################################
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
            school_item['school_language'] = "French"
            school_item['school_type'] = ""
            school_item['school_board'] = "Commission scolaire des Grandes-Seigneuries"
            school_item["response_url"] = response.url
            ######################################################################################
            #extract required data
            school_item["school_name"]	= dom.xpath(school_name_xpath % str(index + 1))
            school_item['street_address'] = dom.xpath(street_address_xpath % str(index + 1))
            data_city_postcode = dom.xpath(data_city_postcode_xpath % str(index + 1))[0].split()
            school_item['city'] = " ".join(data_city_postcode[:-2])
            school_item['province'] = "Québec"
            school_item['postal_code'] = " ".join(data_city_postcode[-2:])
            school_item['phone_number'] = dom.xpath(phone_number_xpath % str(index + 1))
            school_item['school_url'] = dom.xpath(school_url_xpath % str(index + 1))

            yield school_item
