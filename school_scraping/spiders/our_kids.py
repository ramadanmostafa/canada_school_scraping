# -*- coding: utf-8 -*-
import scrapy
from ..items import SchoolScrapingItem


class OurKidsSpider(scrapy.Spider):
    """
    scrapy spider to crawl ourkids.net domain
    you can run it using something like that
    scrapy crawl ourkids_spider
    """
    name = "ourkids_spider"
    allowed_domains = ["ourkids.net"]
    start_urls = (
        'http://www.ourkids.net/montessori-schools.php',
        'http://www.ourkids.net/montessori-schools-ontario.php',
        'http://www.ourkids.net/quebec-private-schools.php',
    )

    def parse(self, response):
        """
        get all links for all schools listed in each page from start_urls tuple including Montessori schools urls or private schools
        """
        #useful xpath strings
        listing1_urls_xpath = '//*[@id="listing1"]/tbody/tr/td[1]/p/strong/a/@href'
        listing2_urls_xpath = '//*[@id="listing2"]/tbody/tr/td[1]/p/strong/a/@href'
        private_schools_urls_xpath = '//*[@id="school_listing"]/tbody/tr/td/div/p/strong/a/@href'
        #############################################################################################
        #get all Montessori schools urls
        all_urls = response.xpath(listing1_urls_xpath).extract() +  response.xpath(listing2_urls_xpath).extract()
        school_board = "Montessori schools"
        if len(all_urls) < 1:
            #this is a page for private schools, then get all private schools urls
            all_urls = response.xpath(private_schools_urls_xpath).extract()
            school_board = "private schools"
        for school_url in all_urls:
            yield scrapy.Request(response.urljoin(school_url), callback = self.parse_school, meta={'board':school_board})

    def parse_school(self, response):
        """
        extract information from pages requested previously in parse method
        """
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
        #some useful xpath variables
        school_url_xpath = '/html/body/div[6]/div[2]/div/div[2]/div[3]/div/p/a/@href'
        school_name_xpath = '/html/body/div[6]/div[1]/div[2]/div/div[2]/h1/text()'
        street_address_xpath = '/html/body/div[7]/div/div[2]/div[2]/span/text()'
        city_xpath = '/html/body/div[6]/div[1]/div[2]/div/div[2]/div[1]/div/div/span[2]/text()'
        province_xpath = '/html/body/div[6]/div[1]/div[2]/div/div[2]/div[1]/div/div/span[3]/text()'
        postal_code_xpath = '/html/body/div[6]/div[1]/div[2]/div/div[2]/div[1]/div/div/span[4]/text()'
        school_grades_xpath = '/html/body/div[6]/div[1]/div[4]/div[2]/text()'
        school_language_xpath = '/html/body/div[6]/div[1]/div[6]/div[2]/text()'
        school_type_xpath = '/html/body/div[6]/div[1]/div[3]/div[2]/text()'
        view_phone_url_xpath = '//*[@id="camp-phone"]/@src'
        ###################################################################
        school_item["response_url"] = response.url
        school_item['school_url'] = response.xpath(school_url_xpath).extract_first()
        school_item["school_name"]	= response.xpath(school_name_xpath).extract_first()
        school_item['street_address'] = response.xpath(street_address_xpath).extract_first().strip().split(',')[0]
        school_item['city'] = response.xpath(city_xpath).extract_first()
        school_item['province'] = response.xpath(province_xpath).extract_first()
        school_item['postal_code'] = response.xpath(postal_code_xpath).extract_first()
        school_item['school_grades'] = response.xpath(school_grades_xpath).extract_first().strip()
        school_item['school_language'] = response.xpath(school_language_xpath).extract_first()
        school_item['school_type'] = response.xpath(school_type_xpath).extract_first()
        school_item['school_board'] = response.meta['board']
        #to get the phone number, it's required to crawl additional 2 pages
        view_phone_url = response.xpath(view_phone_url_xpath).extract_first()
        yield scrapy.Request(view_phone_url, callback = self.get_phone_page, meta={'item':school_item})

    def get_phone_page(self, response):
        """
        method to get the url of the page where we can find the phone number
        """
        phone_number_url_xpath = '/html/body/div/p/a/@href'
        phone_number_url = response.xpath(phone_number_url_xpath).extract_first()
        school_item = response.meta['item']
        yield scrapy.Request(response.urljoin(phone_number_url), callback = self.get_phone_number, meta={'item':school_item})

    def get_phone_number(self, response):
        """
        finally got the phone number of the crawled school
        """
        phone_number_xpath = '/html/body/div/p/text()'
        school_item = response.meta['item']
        school_item['phone_number'] = response.xpath(phone_number_xpath).extract_first()
        yield school_item
