# -*- coding: utf-8 -*-
import scrapy
from ..items import SchoolScrapingItem


class MontrealCspSpider(scrapy.Spider):
    """
    a scrapy spider to crawl csp.ca domain to get
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
    name = "montreal_csp"
    allowed_domains = ["csp.ca"]

    def start_requests(self):
        """
        spider starts from here, crawl url_primary, url_secondary and url_info_centers to get a list of schools urls
        """
        #################################################################
        #start urls
        url_primary = "http://csp.ca/trouver-un-etablissement/primaire/?classement=ville"
        url_secondary = "http://csp.ca/trouver-un-etablissement/secondaire/?classement=ville"
        url_info_centers = "http://csp.ca/trouver-un-etablissement/centre/"
        ####################################################################################################
        #yield a Request for each school type url
        yield scrapy.Request(url_primary, callback=self.parse_list_schools, meta={"type":"école primaire", "grades":"primaire"})
        yield scrapy.Request(url_secondary, callback=self.parse_list_schools, meta={"type":"école secondaire", "grades":"secondaire"})
        yield scrapy.Request(url_info_centers, callback=self.parse_info_centers)

    def parse_info_centers(self, response):
        """
        get required information for each Centre de formation
        this method is called once because all data is found in a single page
        """
        ####################################################################################
        #some useful xpath variables
        num_centers_xpath = '//*[@id="coordonnees"]/div/div/h3/text()'
        school_name_xpath = '//*[@id="coordonnees"]/div/div[%s]/h3/text()'
        street_address_xpath = '//*[@id="coordonnees"]/div/div[%s]/p[1]/text()'
        phone_number_xpath = '//*[@id="coordonnees"]/div/div[%s]/p[4]/text()'
        school_url_xpath = '//*[@id="coordonnees"]/div/div[%s]/p[2]/a/@href'
        ##########################################################################################
        num_centers = len(response.xpath(num_centers_xpath).extract())
        #for each Centre de formation in the page
        for  index in range(num_centers):
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
            school_item['school_grades'] = ""
            school_item['school_language'] = ""
            school_item['school_type'] = "Centre de formation"
            school_item['school_board'] = "Commission scolaire des Patriotes"
            school_item["response_url"] = response.url
            ######################################################################################
            #extract required data
            school_item["school_name"]	= response.xpath(school_name_xpath % str(index + 1)).extract_first()
            full_address = response.xpath(street_address_xpath % str(index + 1)).extract_first()
            school_item['street_address'] = " ".join(full_address.split(",")[:2])
            school_item['city'] = full_address.split(',')[-1].split()[0]
            school_item['postal_code'] = ' '.join(school_item['street_address'].split(',')[-1].split()[-2:])
            school_item['phone_number'] = response.xpath(phone_number_xpath % str(index + 1)).extract_first()
            school_item['school_url'] = response.xpath(school_url_xpath % str(index + 1)).extract_first()

            yield school_item

    def parse_list_schools(self, response):
        """
        get schools pages (primaire and secondaire schools) urls and yield a Request to crawl those pages
        """
        ####################################################################################
        #some useful xpath variables
        all_cities_xpath = '//*[@id="%s"]/h3/text()'
        schools_urls_xpath = '//*[@id="%s"]/ul[%s]/li/nav/a[1]/@href'
        ####################################################################################################
        #detect school type
        if "primaire" in response.meta["type"]:
            school_type = "primaire"
        else:
            school_type = "secondaire"
        #get all cities names
        all_cities = response.xpath(all_cities_xpath % school_type).extract()
        idx_city = 1
        #iterate over each city to get schools urls
        for city in all_cities:
            schools_urls = response.xpath(schools_urls_xpath % (school_type, str(idx_city))).extract()
            for url in schools_urls:
                #yield a Request for each school_url in the current city
                meta = {"type":response.meta["type"], "city":city, "grades":response.meta["grades"]}
                yield scrapy.Request(response.urljoin(url), callback=self.parse_school, meta=meta)
            idx_city += 1

    def parse_school(self, response):
        """
        get required information for each school
        this method is called once for each school
        """
        ####################################################################################
        #some useful xpath variables
        school_name_xpath = '//h1/text()'
        street_address_xpath = '//*[@id="coordonnees-generales"]/p[1]/text()'
        phone_number_xpath = '//*[@id="coordonnees-ecole"]/p[2]/text()'
        school_url_xpath = '//*[@id="coordonnees-generales"]/p[2]/a/@href'
        #####################################################################################
        #init item
        school_item = SchoolScrapingItem()
        school_item["school_name"]	= ""
        school_item['street_address'] = ""
        school_item['city'] = response.meta["city"]
        school_item['province'] = "Québec"
        school_item['postal_code'] = ""
        school_item['phone_number'] = ''
        school_item['school_url'] = ""
        school_item['school_grades'] = response.meta["grades"]
        school_item['school_language'] = "French"
        school_item['school_type'] = response.meta["type"]
        school_item['school_board'] = "Commission scolaire Marie-Victorin"
        school_item["response_url"] = response.url
        ######################################################################################
        #extract required data
        school_item["school_name"]	=  response.xpath(school_name_xpath).extract_first()
        full_address = response.xpath(street_address_xpath).extract_first()
        school_item['street_address'] = " ".join(full_address.split(",")[:2])
        school_item['postal_code'] = " ".join(full_address.split()[-2:])
        school_item['phone_number'] =  response.xpath(phone_number_xpath).extract_first()
        school_item['school_url'] = response.xpath(school_url_xpath).extract_first()

        yield school_item
