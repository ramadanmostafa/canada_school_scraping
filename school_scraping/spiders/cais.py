# -*- coding: utf-8 -*-
import scrapy
from ..items import SchoolScrapingItem
from w3lib.html import remove_tags

class CaisSpider(scrapy.Spider):
    """
    scrapy spider to crawl cais.ca domain
    you can run it using something like that
    scrapy crawl cais
    """
    name = "cais"
    allowed_domains = ["cais.ca"]
    start_urls = (
        'https://www.cais.ca/families/schools',
    )
    custom_settings = {
        "DOWNLOAD_DELAY": 3,
        "CONCURRENT_REQUESTS_PER_DOMAIN":1,
    }

    def parse(self, response):
        """
        get the subpage url that contains the actual search results(schools).
        """
        #some useful xpath variables
        schools_page_url_xpath = '//*[@id="fsEl_420"]/div/iframe/@src'
        schools_page_url = response.xpath(schools_page_url_xpath).extract_first()
        yield scrapy.Request(schools_page_url, callback=self.parse_schools_page)

    def parse_schools_page(self, response):
        """
        this method do exactly 2 jobs:
        1-get school pages urls to be crawled
        2-get next listing page url and call itself again to extract school pages urls
        """
        #some useful xpath variables
        school_pages_xpath = '//*[@id="contentdiv"]/div[2]/font/table[3]/tr/td/font/b/a/@href'
        next_page_urls_xpath = '//*[@id="contentdiv"]/div[2]/font/table[2]/tr[2]/td[2]/font/a/@href'
        school_pages = response.xpath(school_pages_xpath).extract()
        for page_url in school_pages:
            yield scrapy.Request(response.urljoin(page_url), callback=self.parse_school_item)
        next_page_urls = response.xpath(next_page_urls_xpath).extract()
        for next_page_url in next_page_urls:
            yield scrapy.Request(response.urljoin(next_page_url), callback=self.parse_schools_page)

    def parse_school_item(self, response):
        """
        extract information from pages requested previously in parse_schools_page method
        """
        #some useful xpath variables
        school_name_xpath = '//*[@id="contentdiv"]/div[2]/table/tr[2]/td/table/tr[1]/td/h1/text()'
        extracted_lst_xpath = '//*[@id="contentdiv"]/div[2]/table/tr[2]/td/table/tr[%s]'
        #####################################################################
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
        school_item['school_language'] = ""
        school_item['school_type'] = ""
        school_item['school_board'] = ""
        school_item["response_url"] = ""
        ####################################
        school_item["school_name"]	= response.xpath(school_name_xpath).extract_first()
        school_item['school_board'] = "Private schools"
        school_item["response_url"] = response.url
        ###################################################################################
        #index from 1 up to 3 consecutive []
        index = 1
        num_empty = 0
        while num_empty < 3:
            extracted_lst = map(unicode.split, map(remove_tags, response.xpath(extracted_lst_xpath % index).extract()))
            if len(extracted_lst) < 1:
                num_empty += 1
            else:
                num_empty = 0
                if "Website" in extracted_lst[0]:
                    school_item['school_url'] = " ".join(extracted_lst[0][1:])
                elif "Address" in extracted_lst[0]:
                    school_item['street_address'] =  " ".join(extracted_lst[0][2:])
                elif "City" in extracted_lst[0]:
                    school_item['city'] = " ".join(extracted_lst[0][1:])
                elif "Province" in extracted_lst[0]:
                    school_item['province'] = " ".join(extracted_lst[0][1:])
                elif "Postal" in extracted_lst[0]:
                    school_item['postal_code'] = " ".join(extracted_lst[0][2:])
                elif "School" in extracted_lst[0] and "Type" in extracted_lst[0]:
                    school_item['school_type'] = " ".join(extracted_lst[0][2:])
                elif "Phone" in extracted_lst[0]:
                    school_item['phone_number'] = " ".join(extracted_lst[0][1:])
                elif "Grade" in extracted_lst[0]:
                    school_item['school_grades'] = " ".join(extracted_lst[0][2:])

            index += 1
        ###################################################################################
        yield school_item
