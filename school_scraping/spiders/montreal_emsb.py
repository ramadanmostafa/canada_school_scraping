# -*- coding: utf-8 -*-
import scrapy
from ..items import SchoolScrapingItem

class MontrealEmsbSpider(scrapy.Spider):
    """
    a scrapy spider to crawl emsb.qc.ca domain to get
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
    name = "montreal_emsb"
    allowed_domains = ["emsb.qc.ca"]


    def start_requests(self):
        """
        spider starts from here, crawl url_primary, url_secondary and url_edu_center to get a list of schools urls
        """
        #################################################################
        #start urls
        url_primary = "http://www.emsb.qc.ca/emsb_en/schools_en/schools.asp?level=1"
        url_high = "http://www.emsb.qc.ca/emsb_en/schools_en/schools.asp?level=2"
        url_Outreach = "http://www.emsb.qc.ca/emsb_en/schools_en/schools.asp?level=3"
        url_SocialAffairs = "http://www.emsb.qc.ca/emsb_en/schools_en/schools.asp?level=4"
        ####################################################################################################
        #yield a Request for each school type url
        yield scrapy.Request(url_primary, callback=self.parse_list_schools, meta={"type":"Elementary School", "grades":"Elementary"})
        yield scrapy.Request(url_high, callback=self.parse_list_schools, meta={"type":"High School", "grades":"Secondary"})
        yield scrapy.Request(url_Outreach, callback=self.parse_list_schools, meta={"type":"Outreach School", "grades":""})
        yield scrapy.Request(url_SocialAffairs, callback=self.parse_list_schools, meta={"type":"Social Affair", "grades":""})

    def parse_list_schools(self, response):
        """
        get all schools urls then yield a Request for each one.
        """
        ###########################################################################################################
        #some useful xpath variables
        num_schools_xpath = '//*[@id="right-side"]/table/tr[1]/td/a/@href'
        num_schools_xpath2 = '//*[@id="right-side"]/table/tr[2]/td/a/@href'
        ###########################################################################################
        num_schools = response.xpath(num_schools_xpath).extract()
        if len(num_schools) < 1:
            num_schools = response.xpath(num_schools_xpath2).extract()
        for url in num_schools:
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
        this method is called once for each school
        """
        ###########################################################################################################
        #some useful xpath variables
        school_name_xpath1 = '//*[@id="right-side"]/h1/text()'
        school_name_xpath2 = '//*[@id="right-side"]/div/h1/text()'
        street_address_xpath1 = '//*[@id="right-side"]/div/p[1]/font/text()[1]'
        street_address_xpath2 = '//*[@id="right-side"]/p[1]/font/text()[1]'
        full_address_xpath1 = '//*[@id="right-side"]/div/p[1]/font/text()[2]'
        full_address_xpath2 = '//*[@id="right-side"]/p[1]/font/text()[2]'
        data_xpath1 = '//*[@id="right-side"]/div/p[2]/b/text()'
        data_xpath2 = '//*[@id="right-side"]/p[2]/b/text()'
        data_website_xpath1 = '//*[@id="right-side"]/div/p[2]/b/a/@href'
        data_website_xpath2 = '//*[@id="right-side"]/p[2]/b/a/@href'
        school_type_xpath = '/html/head/title/text()'
        #####################################################################################
        #init item
        school_item = SchoolScrapingItem()
        school_item["school_name"]	= ""
        school_item['street_address'] = ""
        school_item['city'] = ""
        school_item['province'] = "QC"
        school_item['postal_code'] = ""
        school_item['phone_number'] = []
        school_item['school_url'] = ""
        school_item['school_grades'] = response.meta["grades"]
        school_item['school_language'] = "English"
        school_item['school_type'] = response.meta["type"]
        school_item['school_board'] = "English Montreal School Board"
        school_item["response_url"] = response.url
        ######################################################################################
        #extract required data
        # school_item['school_type'] = response.xpath(school_type_xpath).extract_first()

        school_item["school_name"]	= response.xpath(school_name_xpath1).extract_first()
        if school_item["school_name"] is None:
            #school name is None which means that school_name_xpath1 doesn't work, lets try the other one
            school_item["school_name"]	= response.xpath(school_name_xpath2).extract_first()
            school_item['street_address'] = response.xpath(street_address_xpath1).extract_first()
            full_address = response.xpath(full_address_xpath1).extract_first().split()
            school_item['city'] = " ".join(full_address[:-2])
            school_item['postal_code'] = " ".join(full_address[-2:])
            data = response.xpath(data_xpath1).extract()
            for item in data:
                if "Phone" in item:
                    school_item['phone_number'].append(item)
            data_website = response.xpath(data_website_xpath1).extract()
            for item in data_website:
                if "@" not in item:
                    school_item['school_url'] += u" " + item
        else:
            school_item['street_address'] = response.xpath(street_address_xpath2).extract_first()
            full_address = response.xpath(full_address_xpath2).extract_first().split()
            school_item['city'] = " ".join(full_address[:-2])
            school_item['postal_code'] = " ".join(full_address[-2:])
            data = response.xpath(data_xpath2).extract()
            for item in data:
                if "Phone" in item:
                    school_item['phone_number'].append(item)
            data_website = response.xpath(data_website_xpath2).extract()
            for item in data_website:
                if "@" not in item:
                    school_item['school_url'] += u" " + item
        school_item["phone_number"] =  " ".join(map(self.digits_only, school_item["phone_number"]))
        yield school_item
