# -*- coding: utf-8 -*-
import scrapy
from ..items import SchoolScrapingItem


class MontrealCspiSpider(scrapy.Spider):
    """
    a scrapy spider to crawl cspi.qc.ca domain to get
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
    name = "montreal_cspi"
    allowed_domains = ["cspi.qc.ca"]

    def start_requests(self):
        """
        spider starts from here, crawl url_primary, url_secondary, url_specialize, url_adults and url_info_prof to get a list of schools urls
        """
        ##################################################################
        #start urls
        url_elementry = 'http://www.cspi.qc.ca/index.php?option=com_mtree&task=listcats&cat_id=44&Itemid=13'
        url_secondary = 'http://www.cspi.qc.ca/index.php?option=com_mtree&task=listcats&cat_id=45&Itemid=13'
        url_specialize = 'http://www.cspi.qc.ca/index.php?option=com_mtree&task=listcats&cat_id=130&Itemid=13'
        url_adults = 'http://www.cspi.qc.ca/index.php?option=com_mtree&task=listcats&cat_id=46&Itemid=13'
        url_info_prof = 'http://www.cspi.qc.ca/index.php?option=com_mtree&task=listcats&cat_id=47&Itemid=22'
        ####################################################################################
        #yield a Request for each url
        yield scrapy.Request(url_elementry, callback=self.parse_schools, meta={"type":"L'école primaire"})
        yield scrapy.Request(url_secondary, callback=self.parse_schools, meta={"type":"L'école secondaire"})
        yield scrapy.Request(url_specialize, callback=self.parse_schools, meta={"type":"Écoles spécialisées"})
        yield scrapy.Request(url_adults, callback=self.parse_schools, meta={"type":"Centres de formation générale des adultes"})
        yield scrapy.Request(url_info_prof, callback=self.parse_schools, meta={"type":"Centres de formation professionnelle"})

    def parse_schools(self, response):
        """
        get required information for each school
        this method is called once for each school type
        """
        ####################################################################################
        #some useful xpath variables
        schools_names_xpath = '//*[@id="listings"]/div/div[2]/a/text()'
        response_urls_xpath = '//*[@id="listings"]/div/div[2]/a/@href'
        street_addresses_xpath = '//*[@id="listings"]/div/div[3]/div/text()[1]'
        postal_codes_xpath = '//*[@id="listings"]/div/div[3]/div/text()[3]'
        school_urls_xpath = '//*[@id="listings"]/div/div[3]/div/a/text()'
        num_schools_css = 'div.mt_item_sublist'
        next_pages_xpath = '//*[@class="pagination"]/li/strong/a/@href'
        ###############################################################################
        #extract data
        schools_names = response.xpath(schools_names_xpath).extract()
        response_urls = response.xpath(response_urls_xpath).extract()
        street_addresses = response.xpath(street_addresses_xpath).extract()
        postal_codes = response.xpath(postal_codes_xpath).extract()
        school_urls = response.xpath(school_urls_xpath).extract()
        num_schools = len(response.css(num_schools_css).extract())
        for i in range(num_schools):
            #####################################################################################
            #init item
            school_item = SchoolScrapingItem()
            school_item["school_name"]	= schools_names[i]
            school_item['street_address'] = street_addresses[i]
            school_item['city'] = "Montréal"
            school_item['province'] = "Québec"
            school_item['postal_code'] = postal_codes[i]
            school_item['phone_number'] = ""
            school_item['school_url'] = school_urls[i]
            school_item['school_grades'] = response.meta["type"]
            school_item['school_language'] = "French"
            school_item['school_type'] = response.meta["type"]
            school_item['school_board'] = "Commission scolaire de la Pointe de l'Ile"
            school_item["response_url"] = response.urljoin(response_urls[i])
            ######################################################################################
            yield scrapy.Request(response.urljoin(response_urls[i]), callback=self.parse_school_profile, meta={"item":school_item})

        #get urls to next pages, it will cause no harm as any duplicates Requests are filtered out
        next_pages = response.xpath(next_pages_xpath).extract()
        for url in next_pages:
            yield scrapy.Request(response.urljoin(url), callback=self.parse_schools, meta=response.meta)


    def parse_school_profile(self, response):
        """
        parse the school profile page to get the missing data (phone number)
        """
        ####################################################################################
        #some useful xpath variables
        phone_number_xpath = '//*[@id="fiche"]/div[3]/div[6]/div[1]/div/text()'
        ####################################################################################
        school_item = response.meta["item"]
        school_item["phone_number"] = response.xpath(phone_number_xpath).extract_first()
        yield school_item
