# -*- coding: utf-8 -*-
import scrapy
from ..items import SchoolScrapingItem


class MontrealCstroisSpider(scrapy.Spider):
    """
    a scrapy spider to crawl cstrois-lacs.qc.ca domain to get
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
    name = "montreal_cstrois"
    allowed_domains = ["cstrois-lacs.qc.ca"]

    def start_requests(self):
        """
        spider starts from here, crawl url_primary and url_secondary to get a list of schools urls
        """
        #################################################################
        #start urls
        url_primary = "http://www.cstrois-lacs.qc.ca/prescolaire-et-primaire/liste-ecoles-primaires"
        url_secondary = "http://www.cstrois-lacs.qc.ca/secondaire/les-ecoles-secondaires"
        ####################################################################################################
        #yield a Request for each school type url
        yield scrapy.Request(url_primary, callback=self.parse_list_schools, meta={"type":"école primaire", "grades":"primaire"})
        yield scrapy.Request(url_secondary, callback=self.parse_list_schools, meta={"type":"école secondaire", "grades":"secondaire"})

    def parse_list_schools(self, response):
        """
        get schools pages urls and yield a Request to crawl those pages
        """
        ####################################################################################
        #some useful xpath variables
        all_schools_urls_xpath = '//*[@id="containerbox"]/div/div/div/div/div[2]/div[2]/div[1]/div[2]/div[3]/div/table/tbody/tr/td[1]/a/@href'
        ####################################################################################
        #yield a Request for each url found
        all_schools_urls = response.xpath(all_schools_urls_xpath).extract()
        for url in all_schools_urls:
            yield scrapy.Request(response.urljoin(url), callback=self.parse_school, meta=response.meta)

    def parse_school(self, response):
        """
        get required information for each school
        this method is called once for each school page
        """
        ####################################################################################
        #some useful xpath variables
        school_name_xpath = '//*[@id="containerbox"]/div/div/div/div/div[2]/div[2]/div[1]/div[2]/div[3]/h1/text()'
        full_address_xpath = '//*[@id="containerbox"]/div/div/div/div/div[2]/div[2]/div[1]/div[2]/div[3]/div/table/tbody/tr/td[1]/p[1]/text()'
        phone_number_xpath = '//*[@id="containerbox"]/div/div/div/div/div[2]/div[2]/div[1]/div[2]/div[3]/div/table/tbody/tr/td[1]/p[2]/text()'
        school_url_xpath = '//*[@id="containerbox"]/div/div/div/div/div[2]/div[2]/div[1]/div[2]/div[3]/div/table/tbody/tr/td[1]/p[2]/a/text()'
        #####################################################################################
        #init item
        school_item = SchoolScrapingItem()
        school_item["school_name"]	= ""
        school_item['street_address'] = ""
        school_item['city'] = ""
        school_item['province'] = "QC"
        school_item['postal_code'] = ""
        school_item['phone_number'] = ''
        school_item['school_url'] = ""
        school_item['school_grades'] = response.meta["grades"]
        school_item['school_language'] = "French"
        school_item['school_type'] = response.meta["type"]
        school_item['school_board'] = "Commission scolaire des Trois-Lacs"
        school_item["response_url"] = response.url
        ######################################################################################
        #extract required data
        school_item["school_name"]	= response.xpath(school_name_xpath).extract_first()
        full_address = response.xpath(full_address_xpath).extract()
        school_item['street_address'] = full_address[0]
        if "QC" in full_address[1]:
            school_item['city'] = full_address[1][:full_address[1].index("QC")]
        school_item['postal_code'] = " ".join(full_address[1].split()[-2:])
        school_item['phone_number'] = response.xpath(phone_number_xpath).extract_first()
        school_item['school_url'] = response.xpath(school_url_xpath).extract_first()

        yield school_item
