# -*- coding: utf-8 -*-
import scrapy
from ..items import SchoolScrapingItem
from w3lib.html import remove_tags


class DpcdsbSpiderSpider(scrapy.Spider):
    name = "dcdsb_spider"
    allowed_domains = ["dcdsb.ca"]
    handle_httpstatus_list = [302, 301]
    start_urls = (
        'http://www.dcdsb.ca/modules/Facilities/Index.aspx',
    )

    def parse(self, response):
        ###########################################################################################
        #some useful xpath variables
        all_schools_urls_xpath = '//*[@id="facilityResultsContainer"]/div[2]/div/div/div/div[1]/div[1]/a/@href'
        school_website_xpath = '//*[@id="facilityResultsContainer"]/div[2]/div[%s]/div[2]/div/div[2]/div/div[3]/a/@href'
        phone_number_xpath = '//*[@id="facilityResultsContainer"]/div[2]/div[%s]/div/div/div/div/div[2]/a/text()'
        next_page_url_xpath = '//*[@id="printAreaContent"]/div/div[5]/div/div/div/a[3]/@href'
        school_name_xpath = '//*[@id="facilityResultsContainer"]/div[2]/div/div/div/div[1]/div[1]/a/text()'
        school_address_xpath = '//*[@id="facilityResultsContainer"]/div[2]/div[%s]/div/div/div[2]/div/div[1]/text()'
        ############################################################################################
        i = 1
        for url in  response.xpath(all_schools_urls_xpath).extract():
            school_website =  response.xpath(school_website_xpath % str(i)).extract_first()
            phone_number = response.xpath(phone_number_xpath % str(i)).extract_first()
            school_name = response.xpath(school_name_xpath).extract()[i-1]
            school_address = response.xpath(school_address_xpath % str(i)).extract_first()
            #####################################################################################
            #init item
            school_item = SchoolScrapingItem()
            school_item["school_name"]	= school_name
            school_item['street_address'] = school_address
            school_item['city'] = ""
            school_item['province'] = "ON"
            school_item['postal_code'] = ""
            school_item['phone_number'] = phone_number
            school_item['school_url'] = school_website
            school_item['school_grades'] = ""
            school_item['school_language'] = ""
            school_item['school_type'] = ""
            school_item['school_board'] = "Durham Catholic District School Board"
            school_item["response_url"] = response.urljoin(url)
            ######################################################################################
            if school_website is not None:
                yield scrapy.Request(response.urljoin(school_website), callback=self.parse_school_website, meta={"item":school_item})
            else:
                yield school_item
            i += 1
        next_page_url = response.xpath(next_page_url_xpath).extract_first()
        yield scrapy.Request(response.urljoin(next_page_url), callback=self.parse)


    def parse_school_website(self, response):
        """
        get some missing information from school webiste, (city, province, postal_code)
        """
        city = '//*[@id="box04"]/p/text()[2]'
        postal_code = '//*[@id="box04"]/p[1]/text()[2]'
        if response.status == 302 or response.status == 301:
            yield scrapy.Request(response.headers["Location"], callback=self.parse_school_website, meta={"item":response.meta["item"]})
        else:
            school_item = response.meta["item"]
            try:
                school_item['city'] = response.xpath(city).extract_first().split(',')[0]
            except:
                school_item['city'] = ""
            try:
                school_item['postal_code'] = ' '.join(response.xpath(postal_code).extract_first().split(',')[1].split()[1:])
            except:
                school_item['postal_code'] = ""
            yield school_item
