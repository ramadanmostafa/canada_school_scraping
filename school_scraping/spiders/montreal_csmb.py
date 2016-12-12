# -*- coding: utf-8 -*-
import scrapy
from ..items import SchoolScrapingItem

class MontrealCsmbSpider(scrapy.Spider):
    """
    a scrapy spider to crawl csmb.qc.ca domain to get
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
    name = "montreal_csmb"
    allowed_domains = ["csmb.qc.ca"]
    start_urls = (
        "http://www.csmb.qc.ca/fr-CA/recherche-etablissement.aspx",
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
        """
        get all schools urls then yield a Request for each one.
        """
        ###########################################################################################################
        #some useful xpath variables
        schools_urls_xpath = '//*[@id="phmain_0_AllResults"]/ul/li/span[1]/a/@href'
        ####################################################################################################
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
        school_name_xpath = '//*[@id="content"]/div[1]/h2/text()'
        street_address_xpath = '//*[@id="content"]/div[2]/div[2]/div/div/p[1]/span/span/text()'
        phone_number_xpath = '//*[@id="content"]/div[2]/div[2]/div/div/p[2]/span[1]/span/text()'
        school_url_xpath = '//*[@id="content"]/div[2]/div[2]/div/a/@href'
        school_type_xpath = '//*[@id="phmain_0_lblSchoolLevel"]/text()'
        #####################################################################################
        #init item
        school_item = SchoolScrapingItem()
        school_item["school_name"]	= ""
        school_item['street_address'] = ""
        school_item['city'] = "Montreal"
        school_item['province'] = "Québec"
        school_item['postal_code'] = ""
        school_item['phone_number'] = ""
        school_item['school_url'] = ""
        school_item['school_grades'] = ""
        school_item['school_language'] = "French"
        school_item['school_type'] = ""
        school_item['school_board'] = "Commission scolaire Marguerite-Bourgeoys"
        school_item["response_url"] = response.url
        ######################################################################################
        #extract required data
        school_item["school_name"]	= response.xpath(school_name_xpath).extract_first().strip()
        tmp_address = response.xpath(street_address_xpath).extract_first()
        school_item['street_address'] = tmp_address.split('(')[0]
        school_item['postal_code'] = " ".join(school_item['street_address'].split()[-2:])
        school_item['phone_number'] = self.digits_only(response.xpath(phone_number_xpath).extract_first())
        school_item['school_url'] = response.xpath(school_url_xpath).extract_first()
        school_item['school_type'] = response.xpath(school_type_xpath).extract_first()
        if "primaire" in school_item['school_type']:
            school_item['school_grades'] = "primaire"
        elif "secondaire" in school_item['school_type']:
            school_item['school_grades'] = "secondaire"
        yield school_item
