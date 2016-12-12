# -*- coding: utf-8 -*-
import scrapy
from ..items import SchoolScrapingItem

class MontrealLbpsbSpider(scrapy.Spider):
    """
    a scrapy spider to crawl lbpsb.qc.ca domain to get
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
    name = "montreal_lbpsb"
    allowed_domains = ["lbpsb.qc.ca"]
    start_urls = (
        "http://www.lbpsb.qc.ca/eng/schools/SchoolsMunicipalityV2.asp",
    )

    def parse(self, response):
        """
        get all schools urls then yield a Request for each one.
        """
        ###########################################################################################################
        #some useful xpath variables
        schools_urls_xpath = '//*[@id="table10"]/tr/td/table[2]/tr/td/font/a/@href'
        ###########################################################################################################
        schools_urls = response.xpath(schools_urls_xpath).extract()
        for url in schools_urls:
            yield scrapy.Request(response.urljoin(url), callback=self.parse_school)

    def parse_school(self, response):
        """
        get required information for each school
        this method is called once for each school
        """
        ###########################################################################################################
        #some useful xpath variables
        school_name_xpath = '//*[@id="table1"]/tr[1]/td/table/tr/td[1]/font/b/text()'
        street_address_xpath = '//*[@id="table1"]/tr[3]/td[1]/font[1]/text()'
        city_xpath = '//*[@id="table1"]/tr[3]/td[1]/font[2]/text()'
        postal_code_xpath = '//*[@id="table1"]/tr[3]/td[1]/font[3]/text()'
        phone_number_xpath = '//*[@id="table1"]/tr[1]/td/table/tr/td[2]/font/b/text()'
        school_url_xpath = '//*[@id="table2"]/tr/td[1]/font/a/@href'
        #####################################################################################
        #init item
        school_item = SchoolScrapingItem()
        school_item["school_name"]	= ""
        school_item['street_address'] = ""
        school_item['city'] = ""
        school_item['province'] = "QC"
        school_item['postal_code'] = ""
        school_item['phone_number'] = ""
        school_item['school_url'] = ""
        school_item['school_grades'] = ""
        school_item['school_language'] = ""
        school_item['school_type'] = ""
        school_item['school_board'] = "Lester B. Pearson School Board"
        school_item["response_url"] = response.url
        ######################################################################################
        #extract data required
        school_item["school_name"]	= response.xpath(school_name_xpath).extract_first().strip()
        school_item['street_address'] = response.xpath(street_address_xpath).extract_first().strip()
        school_item['city'] = response.xpath(city_xpath).extract_first().split(',')[0].strip()
        school_item['postal_code'] = response.xpath(postal_code_xpath).extract_first().strip()
        school_item['phone_number'] = response.xpath(phone_number_xpath).extract_first().strip()
        school_item['school_url'] = response.xpath(school_url_xpath).extract_first().strip()
        yield school_item
