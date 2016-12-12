# -*- coding: utf-8 -*-
import scrapy
from ..items import SchoolScrapingItem


class MontrealCssamaresSpider(scrapy.Spider):
    """
    a scrapy spider to crawl cssamares.qc.ca domain to get
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
    name = "montreal_cssamares"
    allowed_domains = ["cssamares.qc.ca"]

    def digits_only(self, mystring):
        """
        it takes a sting conains some digits then return the only digits
        """
        result = ""
        for ch in mystring:
            if ch.isdigit() or ch == '-':
                result += ch
        return result

    def start_requests(self):
        """
        spider starts from here, crawl url_primary, url_secondary to get a list of schools urls
        """
        #################################################################
        #start urls
        url_elementry = 'http://www.cssamares.qc.ca/?page=primaire'
        url_secondary = 'http://www.cssamares.qc.ca/?page=secondaire'
        ####################################################################################
        #yield a Request for each url
        yield scrapy.Request(url_elementry, callback=self.parse_schools, meta={"type":"L'école primaire", "grades":"primaire"})
        yield scrapy.Request(url_secondary, callback=self.parse_schools, meta={"type":"L'école secondaire", "grades":"secondaire"})

    def parse_schools(self, response):
        """
        get required information for each school
        this method is called once for each school type
        """
        ####################################################################################
        #some useful xpath variables
        school_name_xpath = '//*[@id="cellContenu"]/table/tr[%s]/td[1]/a/text()'
        city_xpath = '//*[@id="cellContenu"]/table/tr[%s]/td[3]/span/text()'
        response_url_xpath = '//*[@id="cellContenu"]/table/tr[%s]/td[1]/a/@href'
        ####################################################################################
        num_schools = len(response.xpath('//*[@id="cellContenu"]/table/tr').extract())
        for i in range(1, num_schools):
            #init item
            school_item = SchoolScrapingItem()
            school_item["school_name"]	= response.xpath(school_name_xpath % str(i + 1)).extract_first()
            school_item['street_address'] = ""
            school_item['city'] = response.xpath(city_xpath % str(i + 1)).extract_first()
            school_item['province'] = "QC"
            school_item['postal_code'] = ""
            school_item['phone_number'] = ""
            school_item['school_url'] = ""
            school_item['school_grades'] = response.meta["grades"]
            school_item['school_language'] = "French"
            school_item['school_type'] = response.meta["type"]
            school_item['school_board'] = "Commission scolaire des Samarres"
            school_item["response_url"] = response.xpath(response_url_xpath % str(i + 1)).extract_first()
            yield scrapy.Request(response.urljoin(school_item["response_url"]), callback=self.parse_school_profile, meta={"item":school_item})

    def parse_school_profile(self, response):
        """
        containue parsing the missing information from school profile page
        """
        ####################################################################################
        #some useful xpath variables
        street_address_xpath1 = '//*[@id="cntContenu_ctl00_etqNoCivique"]/text()'
        street_address_xpath2 = '//*[@id="cntContenu_ctl00_etqRue"]/text()'
        postal_code_xpath = '//*[@id="cntContenu_ctl00_etqCodePostal"]/text()'
        phone_number_xpath = '//*[@id="cntContenu_ctl00_etqTelephone"]/text()'
        ####################################################################################
        school_item = response.meta["item"]
        school_item['street_address'] = response.xpath(street_address_xpath1).extract_first() + " " + response.xpath(street_address_xpath2).extract_first()
        school_item['postal_code'] = response.xpath(postal_code_xpath).extract_first()
        school_item['phone_number'] = self.digits_only(response.xpath(phone_number_xpath).extract_first())
        school_item['school_url'] = response.url
        yield school_item
