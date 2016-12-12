# -*- coding: utf-8 -*-
import scrapy
from ..items import SchoolScrapingItem
from w3lib.html import remove_tags


class MontrealCslavalSpider(scrapy.Spider):
    """
    a scrapy spider to crawl cslaval.qc.ca domain to get
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
    name = "montreal_cslaval"
    allowed_domains = ["cslaval.qc.ca"]

    def start_requests(self):
        """
        spider starts from here, crawl url_primary, url_secondary and url_edu_center to get a list of schools urls
        """
        #################################################################
        #start urls
        url_primary = "http://www2.cslaval.qc.ca/spip.php?rubrique88"
        url_secondary = "http://www2.cslaval.qc.ca/spip.php?rubrique89"
        url_edu_center = "http://www2.cslaval.qc.ca/spip.php?rubrique112"
        ####################################################################################################
        #yield a Request for each school type url
        yield scrapy.Request(url_primary, callback=self.parse_list_schools, meta={"type":"école primaire", "grades":"primaire"})
        yield scrapy.Request(url_secondary, callback=self.parse_list_schools, meta={"type":"école secondaire", "grades":"secondaire"})
        yield scrapy.Request(url_edu_center, callback=self.parse_list_schools, meta={"type":"Centre d’éducation d'adultes", "grades":""})

    def parse_list_schools(self, response):
        """
        get schools pages urls and yield a Request to crawl those pages
        """
        ####################################################################################
        #some useful xpath variables
        all_schools_urls_xpath = '//*[@id="tableauNouvellesServAdmin"]/tr/td/table/tr/td/div/a/@href'
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
        school_name_xpath = '//*[@id="contenuArticle"]/table[2]/tr/td/text()'
        street_address_xpath = '//*[@id="contenuArticle"]/div[1]/p[3]/strong/text()'
        phone_number_xpath = '//*[@id="contenuArticle"]/div[1]/p[4]/strong/text()'
        school_url_xpath = '//*[@id="contenuArticle"]/div[1]/p[4]'
        school_url_xpath2 = '//*[@id="contenuArticle"]/div[1]/p[5]/strong[2]/a/@href'
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
        school_item['school_board'] = "Commission scolaire de Laval"
        school_item["response_url"] = response.url
        ######################################################################################
        #extract required data
        full_address = response.xpath(street_address_xpath).extract_first().split(',')
        school_item["school_name"]	= response.xpath(school_name_xpath).extract_first()
        school_item['street_address'] = " ".join(full_address[:2])
        if len(full_address[-1]) > 2:
            school_item['city'] = full_address[-1].split()[0]
            school_item['postal_code'] = " ".join(full_address[-1].split()[-2:])
        else:
            school_item['city'] = full_address[-2]
            school_item['postal_code'] = full_address[-1]
        school_item['phone_number'] = response.xpath(phone_number_xpath).extract_first()
        school_item['school_url'] = remove_tags(response.xpath(school_url_xpath).extract_first()).strip().split()[-1]
        if "." not in school_item['school_url']:
            school_item['school_url'] = response.xpath(school_url_xpath2).extract_first()
        yield school_item
