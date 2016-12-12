# -*- coding: utf-8 -*-
import scrapy
from ..items import SchoolScrapingItem


class MontrealCsrdnSpider(scrapy.Spider):
    """
    a scrapy spider to crawl csrdn.qc.ca domain to get
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
    name = "montreal_csrdn"
    allowed_domains = ["csrdn.qc.ca"]

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
        spider starts from here, crawl url_primary, url_secondary and url_adults to get a list of schools urls
        """
        #################################################################
        #start urls
        url_elementry = "http://www.csrdn.qc.ca/template.asp?id=84"
        url_secondary = "http://www.csrdn.qc.ca/template.asp?id=85"
        url_adults = "http://www.csrdn.qc.ca/template.asp?id=86"
        ####################################################################################
        #yield a Request for each url
        yield scrapy.Request(url_elementry , callback=self.parse_school, meta={"type":"Préscolaire / primaire", "grades":"primaire"})
        yield scrapy.Request(url_secondary , callback=self.parse_school, meta={"type":"Secondaire", "grades":"Secondaire"})
        yield scrapy.Request(url_adults , callback=self.parse_school, meta={"type":"Formation générale des adultes", "grades":""})

    def parse_school(self, response):
        """
        get required information for each school
        this method is called once for each school type
        """
        ####################################################################################
        #some useful xpath variables
        num_schools_xpath = '/html/body/table/tr[1]/td[2]/table/tr[4]/td[1]/table/tr[3]/td/table[2]/tr'
        school_name_xpath = "/html/body/table/tr[1]/td[2]/table/tr[4]/td[1]/table/tr[3]/td/table[2]/tr[%s]/td[1]/b/a/text()"
        street_address_xpath = "/html/body/table/tr[1]/td[2]/table/tr[4]/td[1]/table/tr[3]/td/table[2]/tr[%s]/td[1]/text()"
        phone_number_xpath = '/html/body/table/tr[1]/td[2]/table/tr[4]/td[1]/table/tr[3]/td/table[2]/tr[%s]/td[2]/text()'
        school_url_xpath = "/html/body/table/tr[1]/td[2]/table/tr[4]/td[1]/table/tr[3]/td/table[2]/tr[%s]/td[1]/b/a/@href"
        #####################################################################################
        num_schools = len(response.xpath(num_schools_xpath).extract())
        for i in range(num_schools):
            #####################################################################################
            #init item
            school_item = SchoolScrapingItem()
            school_item["school_name"]	= ""
            school_item['street_address'] = ""
            school_item['city'] = ""
            school_item['province'] = "Québec"
            school_item['postal_code'] = ""
            school_item['phone_number'] = ""
            school_item['school_url'] = ""
            school_item['school_grades'] = response.meta["grades"]
            school_item['school_language'] = "French"
            school_item['school_type'] = response.meta["type"]
            school_item['school_board'] = "Commission scolaire de la Rivière-du-Nord"
            school_item["response_url"] = response.url
            ######################################################################################
            #extract required data
            school_item["school_name"]	= response.xpath(school_name_xpath % str(i + 1)).extract_first()
            full_address = response.xpath(street_address_xpath % str(i+ 1)).extract_first()
            school_item['street_address'] = " ".join(full_address.split(",")[:2])
            school_item['city'] = full_address.split()[-4]
            school_item['postal_code'] = ' '.join(school_item['street_address'].split()[-2:])
            school_item['phone_number'] = self.digits_only(response.xpath(phone_number_xpath % str(i+ 1)).extract_first())
            school_item['school_url'] = response.urljoin(response.xpath(school_url_xpath % str(i + 1)).extract_first())
            yield school_item
