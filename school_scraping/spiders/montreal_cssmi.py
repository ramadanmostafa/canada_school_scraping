# -*- coding: utf-8 -*-
import scrapy
from ..items import SchoolScrapingItem
from w3lib.html import remove_tags

class MontrealCssmiSpider(scrapy.Spider):
    """
    a scrapy spider to crawl cssmi.qc.ca domain to get
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
    name = "montreal_cssmi"
    allowed_domains = ["cssmi.qc.ca"]
    start_urls = (
        "https://www.cssmi.qc.ca/",
    )

    def parse(self, response):
        """
        crawl the initial page to get a list of urls for all schools.
        schools urls are collected based on thier type
        """
        ###########################################################################################################
        #some useful xpath variables
        urls_primary_xpath = '//*[@id="sltEcoPrim"]/option/@value'
        urls_secondary_xpath = '//*[@id="sltEcoSec"]/option/@value'
        urls_info_centers_xpath = '//*[@id="sltCenForm"]/option/@value'
        #######################################################################################################
        urls_primary = response.xpath(urls_primary_xpath).extract()
        urls_secondary = response.xpath(urls_secondary_xpath).extract()
        urls_info_centers = response.xpath(urls_info_centers_xpath).extract()

        for url in urls_primary:
            yield scrapy.Request(response.urljoin(url), callback=self.parse_school, meta={"type":"école primaire", "grades":"primaire"})

        for url in urls_secondary:
            yield scrapy.Request(response.urljoin(url), callback=self.parse_school, meta={"type":"école secondaire", "grades":"secondaire"})

        for url in urls_info_centers:
            yield scrapy.Request(response.urljoin(url), callback=self.parse_school, meta={"type":"un centre de information", "grades":""})

    def digits_only(self, mystring):
        """
        it takes a sting conains some digits then return the only digits
        """
        result = ""
        for ch in mystring:
            if ch.isdigit() or ch == '-':
                result += ch
            elif len(result) > 9:
                return result
        return result

    def parse_school(self, response):
        """
        get required information for each school
        this method is called once for each school page
        """
        ####################################################################################
        #some useful xpath variables
        school_name = '//div/h3/text()'
        full_address = '//div/h1[1]/text()'
        data_tags = '//div/h1[3]'
        school_url = '//div[%s]/h1[4]/a[1]/@href'
        #######################################################################################
        num_schools = len(response.xpath('//h3/text()').extract())
        for  index in range(num_schools):
            #####################################################################################
            #init item
            school_item = SchoolScrapingItem()
            school_item["school_name"]	= ""
            school_item['street_address'] = ""
            school_item['city'] = ""
            school_item['province'] = "Québec"
            school_item['postal_code'] = ""
            school_item['phone_number'] = ''
            school_item['school_url'] = ""
            school_item['school_grades'] = response.meta["grades"]
            school_item['school_language'] = "French"
            school_item['school_type'] = response.meta["type"]
            school_item['school_board'] = "Commission scolaire de la Seigneurie-des-Mille-Îles"
            school_item["response_url"] = response.url
            ######################################################################################
            #extract required data
            school_item["school_name"]	= response.xpath(school_name).extract()[index]
            full_address = response.xpath(full_address).extract()
            school_item['street_address'] = full_address[0 + 2 * index]
            school_item['city'] = full_address[1 + 2 * index].split(',')[0]
            school_item['postal_code'] = full_address[1 + 2 * index].split(',')[1]
            data_tags = response.xpath(data_tags).extract()
            data = map(remove_tags, data_tags)
            data_striped = map(unicode.strip, data)
            data_filtered = filter(None, data_striped)
            school_item['phone_number'] = self.digits_only(data_filtered[index])
            school_item['school_url'] = response.xpath(school_url % str(2 + index)).extract_first()

            yield school_item
