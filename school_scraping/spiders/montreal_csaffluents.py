# -*- coding: utf-8 -*-
import scrapy
from ..items import SchoolScrapingItem
from w3lib.html import remove_tags


class MontrealCsaffluentsSpider(scrapy.Spider):
    """
    a scrapy spider to crawl csaffluents.qc.ca domain to get
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
    name = "montreal_csaffluents"
    allowed_domains = ["csaffluents.qc.ca"]

    def start_requests(self):
        """
        spider starts from here, crawl url_primary, url_secondary and url_edu_center to get a list of schools urls
        """
        #################################################################
        #start urls
        url_primary = "https://www.csaffluents.qc.ca/spip.php?rubrique25"
        url_secondary = "https://www.csaffluents.qc.ca/spip.php?rubrique26"
        url_formation_professional = "https://www.csaffluents.qc.ca/spip.php?rubrique63"
        url_formation_adult = "https://www.csaffluents.qc.ca/spip.php?rubrique64"
        ####################################################################################################
        #yield a Request for each school type url
        yield scrapy.Request(url_primary, callback=self.parse_list_schools, meta={"type":"école primaire", "grades":"primaire"})
        yield scrapy.Request(url_secondary, callback=self.parse_list_schools, meta={"type":"école secondaire", "grades":"secondaire"})
        yield scrapy.Request(url_formation_professional, callback=self.parse_list_schools, meta={"type":"Formation professionnelle", "grades":""})
        yield scrapy.Request(url_formation_adult, callback=self.parse_list_schools, meta={"type":"Formation générale des adultes", "grades":""})

    def parse_list_schools(self, response):
        """
        get schools pages urls and yield a Request to crawl those pages
        """
        ####################################################################################
        #some useful xpath variables
        all_schools_urls_xpath = '//*[@id="pageColumn2"]/ul/li/a/@href'
        ####################################################################################
        #yield a Request for each url found
        all_schools_urls = response.xpath(all_schools_urls_xpath).extract()
        for url in all_schools_urls:
            yield scrapy.Request(response.urljoin(url), callback=self.parse_school, meta=response.meta)

    def digits_only(self, mystring):
        """
        it takes a sting conains some digits then return the only digits
        """
        result = ""
        for ch in mystring:
            if ch.isdigit() or ch == '-':
                result += ch
        return result

    def parse_school(self, response):
        """
        get required information for each school
        this method is called once for each school page
        """
        ####################################################################################
        #some useful xpath variables
        school_name_xpath = '//*[@id="pageColumn2"]/h2/text()'
        details_xpath = '//*[@id="pageColumn2"]/div[1]/p[1]/text()'
        data_xpath = '//*[@id="pageColumn2"]/div'
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
        school_item['school_board'] = "Commission scolaire des Affluents"
        school_item["response_url"] = response.url
        ######################################################################################
        #extract required data
        school_item["school_name"]	= response.xpath(school_name_xpath).extract_first()
        details = response.xpath(details_xpath).extract()
        school_item['street_address'] = details[0]
        school_item['city'] = details[1].split(',')[0]
        school_item['postal_code'] = ' '.join(details[1].split()[-2:])
        school_item['phone_number'] = self.digits_only(details[2])
        data = remove_tags(response.xpath(data_xpath).extract_first()).strip().split()
        if 'Site' in data:
            school_item['school_url'] = data[data.index('Site') + 2]

        yield school_item
