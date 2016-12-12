# -*- coding: utf-8 -*-
import scrapy
from ..items import SchoolScrapingItem

class MontrealCsvtSpider(scrapy.Spider):
    """
    a scrapy spider to crawl csvt.qc.ca domain to get
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
    name = "montreal_csvt"
    allowed_domains = ["csvt.qc.ca"]
    start_urls = (
        'http://www.csvt.qc.ca/prescolaire-primaire-et-secondaire/les-ecoles',
    )

    def digits_only(self, mystring):
        """
        it takes a sting conains some digits then return the only digits
        """
        result = ""
        for ch in mystring:
            if ch.isdigit() or ch == '-':
                result += ch
        return result

    def parse(self, response):
        """
        parse the start page to get required information for all schools found.
        it parses each school type independently.
        """
        ###########################################################################################################
        #some useful xpath variables
        num_schools_primary_xpath = '//*[@id="col_left"]/div[3]/table[1]/tbody/tr'
        full_address_primary_xpath = '//*[@id="col_left"]/div[3]/table[1]/tbody/tr[%s]/td[1]/text()'
        school_name_primary_xpath = '//*[@id="col_left"]/div[3]/table[1]/tbody/tr[%s]/td[1]/strong/text()'
        num_schools_primary_secondary_xpath = '//*[@id="col_left"]/div[3]/table[2]/tbody/tr'
        full_address_primary_secondary_xpath = '//*[@id="col_left"]/div[3]/table[2]/tbody/tr[%s]/td[1]/text()'
        school_name_primary_secondary_xpath = '//*[@id="col_left"]/div[3]/table[2]/tbody/tr[%s]/td[1]/strong/text()'
        num_schools_secondary_xpath = '//*[@id="col_left"]/div[3]/table[3]/tbody/tr'
        full_address_phone_secondary_xpath = '//*[@id="col_left"]/div[3]/table[3]/tbody/tr[%s]/td[1]/text()'
        school_name_secondary_xpath = '//*[@id="col_left"]/div[3]/table[3]/tbody/tr[%s]/td[1]/strong/text()'
        num_centers_xpath = '//*[@id="col_left"]/div[4]/table[3]/tbody/tr'
        full_address_phone_centers_xpath = '//*[@id="col_left"]/div[3]/table[4]/tbody/tr[%s]/td[1]/text()'
        school_name_centers_xpath = '//*[@id="col_left"]/div[3]/table[4]/tbody/tr[%s]/td[1]/strong/text()'
        num_centers_professionals_xpath = '//*[@id="col_left"]/div[3]/table[5]/tbody/tr'
        full_address_phone_centers_professionals_xpath = '//*[@id="col_left"]/div[3]/table[5]/tbody/tr[%s]/td[1]/text()'
        school_name_centers_professionals_xpath = '//*[@id="col_left"]/div[3]/table[5]/tbody/tr[%s]/td[1]/strong/text()'
        ##########################################################################################################
        num_schools_primary = len(response.xpath(num_schools_primary_xpath).extract())
        for i in range(1, num_schools_primary):
            #init item
            school_item = SchoolScrapingItem()
            full_address = response.xpath(full_address_primary_xpath % str(i+1)).extract()
            school_item["school_name"]	= response.xpath(school_name_primary_xpath % str(i+1)).extract_first()
            school_item['street_address'] = ' '.join(full_address[0].split()[:-3])
            school_item['city'] = full_address[0].split()[-3]
            school_item['province'] = "QC"
            school_item['postal_code'] = ' '.join(full_address[0].split()[-2:])
            school_item['phone_number'] = self.digits_only(full_address[3])
            school_item['school_url'] = ""
            school_item['school_grades'] = "primaire"
            school_item['school_language'] = "French"
            school_item['school_type'] = "École primaire"
            school_item['school_board'] = "Commission scolaire de la Vallée-des-Tisserands"
            school_item["response_url"] = response.url
            yield school_item

        num_schools_primary_secondary = len(response.xpath(num_schools_primary_secondary_xpath).extract())
        for i in range(1, num_schools_primary_secondary):
            #init item
            school_item = SchoolScrapingItem()
            full_address = response.xpath(full_address_primary_secondary_xpath % str(i+1)).extract()
            school_item["school_name"]	= response.xpath(school_name_primary_secondary_xpath % str(i+1)).extract_first()
            school_item['street_address'] = ' '.join(full_address[0].split()[:-3])
            school_item['city'] = full_address[0].split()[-3]
            school_item['province'] = "QC"
            school_item['postal_code'] = ' '.join(full_address[0].split()[-2:])
            school_item['phone_number'] = self.digits_only(full_address[4])
            school_item['school_url'] = ""
            school_item['school_grades'] = "secondaire"
            school_item['school_language'] = "French"
            school_item['school_type'] = "École primaire et secondaire"
            school_item['school_board'] = "Commission scolaire de la Vallée-des-Tisserands"
            school_item["response_url"] = response.url
            yield school_item

        num_schools_secondary = len(response.xpath(num_schools_secondary_xpath).extract())
        for i in range(1, num_schools_secondary):
            #init item
            school_item = SchoolScrapingItem()
            full_address_phone = response.xpath(full_address_phone_secondary_xpath % str(i+1)).extract()
            school_item["school_name"]	= response.xpath(school_name_secondary_xpath % str(i+1)).extract_first()
            school_item['street_address'] = ' '.join(full_address_phone[0].split()[:-3])
            school_item['city'] = full_address_phone[0].split()[-3]
            school_item['province'] = "QC"
            school_item['postal_code'] = ' '.join(full_address_phone[0].split()[-2:])
            school_item['phone_number'] = self.digits_only(full_address_phone[4])
            school_item['school_url'] = ""
            school_item['school_grades'] = "secondaire"
            school_item['school_language'] = "French"
            school_item['school_type'] = "Écoles secondaires"
            school_item['school_board'] = "Commission scolaire de la Vallée-des-Tisserands"
            school_item["response_url"] = response.url
            yield school_item

        num_centers = len(response.xpath(num_centers_xpath).extract())
        for i in range(1, num_centers):
            #init item
            school_item = SchoolScrapingItem()
            full_address_phone = response.xpath(full_address_phone_centers_xpath % str(i+1)).extract()
            school_item["school_name"]	= response.xpath(school_name_centers_xpath % str(i+1)).extract_first()
            if i==1:
                school_item['street_address'] = full_address_phone[0]
                school_item['postal_code'] = full_address_phone[1]
            else:
                school_item['street_address'] = ' '.join(full_address_phone[0].split()[:-3])
                school_item['postal_code'] = ' '.join(full_address_phone[0].split()[-2:])

            school_item['phone_number'] = self.digits_only(full_address_phone[4])
            school_item['city'] = ""
            school_item['province'] = "QC"
            school_item['school_url'] = ""
            school_item['school_grades'] = ""
            school_item['school_language'] = "French"
            school_item['school_type'] = "Les centres intégrés du Nouvel-Envol"
            school_item['school_board'] = "Commission scolaire de la Vallée-des-Tisserands"
            school_item["response_url"] = response.url
            yield school_item

        num_centers_professionals = len(response.xpath(num_centers_professionals_xpath).extract())
        for i in range(1, num_centers_professionals):
            #init item
            school_item = SchoolScrapingItem()
            full_address_phone = response.xpath(full_address_phone_centers_professionals_xpath % str(i+1)).extract()
            school_item["school_name"]	= response.xpath(school_name_centers_professionals_xpath % str(i+1)).extract_first()
            school_item['street_address'] = full_address_phone[0]
            school_item['city'] = ""
            school_item['province'] = "QC"
            school_item['postal_code'] = ' '.join(full_address_phone[1].split()[-2:])
            if "c" in full_address_phone[-2]:
                school_item['phone_number'] = self.digits_only(full_address_phone[-3])
            else:
                school_item['phone_number'] = self.digits_only(full_address_phone[-2])

            school_item['school_url'] = ""
            school_item['school_grades'] = ""
            school_item['school_language'] = "French"
            school_item['school_type'] = "Centres de formation professionnelle"
            school_item['school_board'] = "Commission scolaire de la Vallée-des-Tisserands"
            school_item["response_url"] = response.url
            yield school_item
