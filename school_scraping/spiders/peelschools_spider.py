# -*- coding: utf-8 -*-
import scrapy
from ..items import SchoolScrapingItem


class PeelschoolsSpiderSpider(scrapy.Spider):
    name = "peelschools_spider"
    allowed_domains = ["peelschools.org"]
    handle_httpstatus_list = [302]

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
        generate a list of requests to get all listing schools from A-W
        """
        url_start = 'http://www.peelschools.org/schools/all/Pages/default.aspx?psb-letter='
        letters_list = [
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
            "I",
            "J",
            "K",
            "L",
            "M",
            "N",
            "O",
            "P",
            "Q",
            "R",
            "S",
            "T",
            "V",
            "W",
        ]
        for letter in letters_list:
            yield scrapy.Request(url_start + letter, callback=self.parse_all_schools)

    def parse_all_schools(self, response):
        """
        extract a list of schools profiles urls to be parsed
        """
        ###########################################################################################
        #some useful xpath variables
        schools_profiles_urls_xpath = '//*[@id="ctl00_PlaceHolderMain_dynamicContentControlMain"]/div/div/table/tr/td/div/a/@href'
        ####################################################################################
        schools_profiles_urls = response.xpath(schools_profiles_urls_xpath).extract()
        for url in schools_profiles_urls:
            yield scrapy.Request(response.urljoin(url), callback=self.parse_school)

    def parse_school(self, response):
        """
        parse each school profile to get required information
        """
        ###########################################################################################
        #some useful xpath variables
        tmp_address_xpath = '//*[@id="ctl00_PlaceHolderMain_ctl00_zlblAddress2"]/text()'
        school_name_xpath = '//*[@id="ctl00_PlaceHolderMain_ctl00_zlblSchoolName"]/text()'
        street_address_xpath = '//*[@id="ctl00_PlaceHolderMain_ctl00_zlblAddress1"]/text()'
        phone_number_xpath = '//*[@id="ctl00_PlaceHolderMain_ctl00_zlblPhone"]/text()'
        school_url_xpath = '//*[@id="ctl00_PlaceHolderMain_ctl00_zlnkWebSite"]/@href'
        school_info_url_xpath = '//*[@id="ctl00_PlaceHolderMain_ctl00_zlnkSchoolInfo"]/@href'
        ####################################################################################
        #init item
        school_item = SchoolScrapingItem()
        school_item["school_name"]	= ''
        school_item['street_address'] = ''
        school_item['city'] = ""
        school_item['province'] = ""
        school_item['postal_code'] = ""
        school_item['phone_number'] = ""
        school_item['school_url'] = ""
        school_item['school_grades'] = ""
        school_item['school_language'] = ""
        school_item['school_type'] = ""
        school_item['school_board'] = "Peel District School Board"
        school_item["response_url"] = response.url
        ##########################################################################################################
        tmp_address = response.xpath(tmp_address_xpath).extract_first()
        school_item["school_name"]	= response.xpath(school_name_xpath).extract_first()
        school_item['street_address'] = response.xpath(street_address_xpath).extract_first()
        school_item['city'] = tmp_address.split(',')[0]
        school_item['province'] = tmp_address.split(',')[1].split()[0]
        school_item['postal_code'] = tmp_address.split(',')[1].split()[1]
        school_item['phone_number'] = self.digits_only(response.xpath(phone_number_xpath).extract_first())
        school_item['school_url'] = response.xpath(school_url_xpath).extract_first()
        school_item['school_type'] = ' '.join(school_item["school_name"].split()[-2:])

        school_info_url = response.xpath(school_info_url_xpath).extract_first()
        try:
            yield scrapy.Request(school_info_url, callback=self.get_school_grades, meta = {"item": school_item})
        except:
            yield school_item

    def get_school_grades(self, response):
        """
        parse the school website to get school_grades
        """
        ###########################################################################################
        #some useful xpath variables
        school_grades_xpath = '//*[@id="ctl00_PlaceHolderMain_dynamicContentControlMain"]/div/table[4]/tr/td[1]/span/text()'
        ####################################################################################
        if response.status == 302:
            yield scrapy.Request(
                response.headers["Location"],
                callback=self.get_school_grades,
                meta = {"item": response.meta["item"]}
            )
        else:
            school_item = response.meta["item"]
            school_item['school_grades'] = " ".join(response.xpath(school_grades_xpath).extract())
            yield school_item
