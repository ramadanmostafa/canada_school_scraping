# -*- coding: utf-8 -*-
import scrapy
from ..items import SchoolScrapingItem
from w3lib.html import remove_tags

class MontrealCsmvSpider(scrapy.Spider):
    """
    a scrapy spider to crawl csmv.qc.ca domain to get
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
    name = "montreal_csmv"
    allowed_domains = ["csmv.qc.ca"]
    start_urls = (
        "https://www.csmv.qc.ca/la-csmv/nos-etablissements/",
    )

    def parse(self, response):
        """
        crawl the initial page to get a list of urls for all schools.
        schools urls are collected based on thier type
        """
        ###########################################################################################################
        #some useful xpath variables
        url_primary_xpath = '//*[@id="accordion-1-c1"]/table/tbody/tr/td[1]/a/@href'
        url_secondary_xpath = '//*[@id="accordion-2-c1"]/table/tbody/tr/td[1]/a/@href'
        url_professional_training_xpath = '//*[@id="accordion-3-c1"]/table/tbody/tr/td[1]/a/@href'
        url_adult_education_xpath = '//*[@id="accordion-4-c1"]/table/tbody/tr/td[1]/a/@href'
        url__pecialized_school_primary_xpath = '//*[@id="accordion-5-c1"]/table[1]/tbody/tr/td[1]/a/@href'
        url__pecialized_school_secondary_xpath = '//*[@id="accordion-5-c1"]/table[2]/tbody/tr/td[1]/a/@href'
        ############################################################################################################
        #get list of schools pages urls for each type
        url_primary = response.xpath(url_primary_xpath).extract()
        url_secondary = response.xpath(url_secondary_xpath).extract()
        url_professional_training = response.xpath(url_professional_training_xpath).extract()
        url_adult_education = response.xpath(url_adult_education_xpath).extract()
        url__pecialized_school_primary = response.xpath(url__pecialized_school_primary_xpath).extract()
        url__pecialized_school_secondary = response.xpath(url__pecialized_school_secondary_xpath).extract()
        ###############################################################################################################
        #meta variables
        meta_primary = {
            "type":"Primary school",
            "grades":"primaire",
        }
        meta_secondary = {
            "type":"Secondary school",
            "grades":"Secondary",
        }
        meta_professional_training = {
            "type":"Professional Training",
            "grades":"",
        }
        meta_adult_education = {
            "type":"Adult Education",
            "grades":"",
        }
        meta_pecialized_school_primary = {
            "type":"Specialized School(Primary)",
            "grades":"primaire",
        }
        meta_pecialized_school_secondary = {
            "type":"Specialized School(Secondary)",
            "grades":"Secondary",
        }
        ###############################################################################################################
        #iterate on each type list and yield a Request to crawl the page
        for url in url_primary:
            yield scrapy.Request(response.urljoin(url), callback=self.parse_school, meta=meta_primary)

        for url in url_secondary:
            yield scrapy.Request(response.urljoin(url), callback=self.parse_school, meta=meta_secondary)

        for url in url_professional_training:
            yield scrapy.Request(response.urljoin(url), callback=self.parse_school, meta=meta_professional_training)

        for url in url_adult_education:
            yield scrapy.Request(response.urljoin(url), callback=self.parse_school, meta=meta_adult_education)

        for url in url__pecialized_school_primary:
            yield scrapy.Request(response.urljoin(url), callback=self.parse_school, meta=meta_pecialized_school_primary)

        for url in url__pecialized_school_secondary:
            yield scrapy.Request(response.urljoin(url), callback=self.parse_school, meta=meta_pecialized_school_secondary)

    def digits_only(self, mystring):
        """
        it takes a sting conains some digits then return the only digits
        """
        result = ""
        for ch in mystring:
            if ch.isdigit() or ch == '-':
                result += ch
        return result

    def parse_school(self, response):
        """
        get required information for each school
        this method is called once for each school
        """
        ####################################################################################
        #some useful xpath variables
        school_name_xpath = '//h1/text()'
        data_xpath = '//*[@id="col_principal"]/div'
        school_url_xpath = '//a[text()="Site internet"]/@href'
        #####################################################################################
        #init item
        school_item = SchoolScrapingItem()
        school_item["school_name"]	= ""
        school_item['street_address'] = ""
        school_item['city'] = ""
        school_item['province'] = ""
        school_item['postal_code'] = ""
        school_item['phone_number'] = ''
        school_item['school_url'] = ""
        school_item['school_grades'] = response.meta["grades"]
        school_item['school_language'] = "French"
        school_item['school_type'] = response.meta["type"]
        school_item['school_board'] = "Commission scolaire Marie-Victorin"
        school_item["response_url"] = response.url
        ######################################################################################
        #get the street_address, city, province, postal_code, phone_number then clean and filter out empty strings
        school_item["school_name"]	= response.xpath(school_name_xpath).extract_first()
        data_tags = response.xpath(data_xpath).extract_first()
        data_unclean = remove_tags(data_tags).strip().split("\n")
        data_clean = map(unicode.strip, data_unclean)
        data = filter(None, data_clean)
        ########################################################################################
        #extract required data
        for index in range(len(data)):
            if self.hasNumbers(data[index]):
                #first item in data list has a digit is the address for sure
                school_item['street_address'] = data[index]
                tmp = data[index + 1].split(',')
                school_item['city'] = tmp[0]
                school_item['province'] = "QC"
                school_item['postal_code'] = tmp[1]
                school_item['phone_number'] = self.digits_only(data[index + 2])
                break
        school_item['school_url'] = response.xpath(school_url_xpath).extract_first()
        yield school_item

    def hasNumbers(self, inputString):
        """
        helper function that checks if some sting contains a digit or not
        return True or False.
        """
        return any(char.isdigit() for char in inputString)
