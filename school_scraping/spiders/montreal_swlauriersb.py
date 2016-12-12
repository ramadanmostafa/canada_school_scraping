# -*- coding: utf-8 -*-
import scrapy
from ..items import SchoolScrapingItem


class MontrealSwlauriersbSpider(scrapy.Spider):
    """
    a scrapy spider to crawl swlauriersb.qc.ca domain to get
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
    name = "montreal_swlauriersb"
    allowed_domains = ["swlauriersb.qc.ca"]
    start_urls = (
        'http://www.swlauriersb.qc.ca/?page=schools/overviewschools',
    )

    def parse(self, response):
        """
        parse the start urls to get a list of schools urls for all schools types and cities
        """
        ####################################################################################
        #some useful xpath variables
        num_schools_elementary_laval_xpath = '//*[@id="MainContent"]/div[1]/p[2]/a/@href'
        num_schools_secondary_laval_xpath = '//*[@id="MainContent"]/div[1]/p[4]/a/@href'
        num_schools_elementary_lanaudiere1_xpath = '//*[@id="MainContent"]/div[1]/p[8]/a/@href'
        num_schools_secondary_lanaudiere1_xpath = '//*[@id="MainContent"]/div[1]/p[10]/a/@href'
        num_schools_elementary_lanaudiere2_xpath = '//*[@id="MainContent"]/div[2]/p[2]/a/@href'
        num_schools_secondary_lanaudiere2_xpath = '//*[@id="MainContent"]/div[2]/p[4]/a/@href'
        ####################################################################################
        #extract number of different schools in different cities
        num_schools_elementary_laval = response.xpath(num_schools_elementary_laval_xpath).extract()
        num_schools_secondary_laval = response.xpath(num_schools_secondary_laval_xpath).extract()
        num_schools_elementary_lanaudiere1 = response.xpath(num_schools_elementary_lanaudiere1_xpath).extract()
        num_schools_secondary_lanaudiere1 = response.xpath(num_schools_secondary_lanaudiere1_xpath).extract()
        num_schools_elementary_lanaudiere2 = response.xpath(num_schools_elementary_lanaudiere2_xpath).extract()
        num_schools_secondary_lanaudiere2 = response.xpath(num_schools_secondary_lanaudiere2_xpath).extract()
        #######################################################################################
        #yield Requests to get all schools
        for url in num_schools_elementary_laval:
            yield scrapy.Request(response.urljoin(url), callback=self.parse_school_profile, meta={"city":"Laval", "type":"Elementary School", "grades":"Elementary"})

        for url in num_schools_secondary_laval:
            yield scrapy.Request(response.urljoin(url), callback=self.parse_school_profile, meta={"city":"Laval", "type":"Secondary School", "grades":"Secondary"})

        for url in num_schools_elementary_lanaudiere1:
            yield scrapy.Request(response.urljoin(url), callback=self.parse_school_profile, meta={"city":"Lanaudière", "type":"Elementary School", "grades":"Elementary"})

        for url in num_schools_secondary_lanaudiere1:
            yield scrapy.Request(response.urljoin(url), callback=self.parse_school_profile, meta={"city":"Lanaudière", "type":"Secondary School", "grades":"Secondary"})

        for url in num_schools_elementary_lanaudiere2:
            yield scrapy.Request(response.urljoin(url), callback=self.parse_school_profile, meta={"city":"Laurentides", "type":"Elementary School", "grades":"Elementary"})

        for url in num_schools_secondary_lanaudiere2:
            yield scrapy.Request(response.urljoin(url), callback=self.parse_school_profile, meta={"city":"Laurentides", "type":"Secondary School", "grades":"Secondary"})


    def parse_school_profile(self, response):
        """
        get required information for each school
        this method is called once for each school page
        """
        ####################################################################################
        #some useful xpath variables
        school_name_xpath = '//*[@id="commissionerRight"]/h3/text()'
        street_address_xpath = '//*[@id="commissionerLeft"]/div/p[1]/text()[1]'
        postal_code_xpath = '//*[@id="commissionerLeft"]/div/p[1]/text()[3]'
        phone_number_xpath = '//*[@id="commissionerLeft"]/div/p[1]/text()[4]'
        school_url_xpath = '//*[@id="commissionerLeft"]/div/p[2]/a/@href'
        #####################################################################################
        #init item
        school_item = SchoolScrapingItem()
        school_item["school_name"]	= ""
        school_item['street_address'] = ""
        school_item['city'] = response.meta["city"]
        school_item['province'] = "QC"
        school_item['postal_code'] = ""
        school_item['phone_number'] = ""
        school_item['school_url'] = ""
        school_item['school_grades'] = response.meta["grades"]
        school_item['school_language'] = "English"
        school_item['school_type'] = response.meta["type"]
        school_item['school_board'] = "Sir Wilfred Laurier School Board"
        school_item["response_url"] = response.url
        ######################################################################################
        school_item["school_name"]	= response.xpath(school_name_xpath).extract_first().strip()
        school_item['street_address'] = response.xpath(street_address_xpath).extract_first().strip()
        school_item['postal_code'] = response.xpath(postal_code_xpath).extract_first().strip()
        school_item['phone_number'] = self.digits_only(response.xpath(phone_number_xpath).extract_first())
        school_item['school_url'] = response.xpath(school_url_xpath).extract_first()
        yield school_item

    def digits_only(self, mystring):
        """
        it takes a sting conains some digits then return the only digits
        """
        result = ""
        for ch in mystring:
            if ch.isdigit() or ch == '-':
                result += ch
        return result
