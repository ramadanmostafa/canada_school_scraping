# -*- coding: utf-8 -*-
import scrapy
from ..items import SchoolScrapingItem
from selenium import webdriver
import lxml.html
import time


class MontrealRechercheetabSpider(scrapy.Spider):
    """
    this spider uses selenium mainly.
    a scrapy spider to crawl rechercheetab.csdm.qc.ca domain to get
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
    name = "montreal_rechercheetab"
    allowed_domains = ["rechercheetab.csdm.qc.ca"]
    start_urls = (
        "http://rechercheetab.csdm.qc.ca/Rechercheetablissement.aspx?recherche=nomecole&nom=&niveau=PR",
    )

    def parse(self, response):
        """
        this method uses selenium to get data for all schools from a single page, it follows this routine
        1-init a selenium driver to get the page url
        2-select search all schools then press the search button
        3-iterate on each result of the search query and do the following:
        3.1-click on the school link
        3.2-get required data
        4-close the driver when finished
        """
        ###########################################################################################################
        #some useful xpath variables
        select_search_all_xpath = '//*[@id="ddlOrder"]/option[1]'
        frame_results_xpath = '//*[@id="iframeResults"]'
        num_schools_xpath = '/html/body/a'
        school_link_xpath = '/html/body/a[%s]'
        school_name_xpath = '//*[@id="schoolCoordonates"]/tbody/tr[1]/td/b/text()'
        street_address_xpath = '//*[@id="schoolCoordonates"]/tbody/tr[2]/td[2]/span/text()'
        postal_code_xpath = '//*[@id="schoolCoordonates"]/tbody/tr[2]/td[2]/text()[1]'
        phone_number_xpath = '//*[@id="schoolCoordonates"]/tbody/tr[2]/td[2]/text()[2]'
        school_url_xpath = '//*[@id="schoolCoordonates"]/tbody/tr[2]/td[2]/span/a/@href'
        school_type_xpath = '//*[@id="ucGoogleMap_googleMap"]/div[1]/div/div[1]/div[4]/div[4]/div[2]/div[2]/div/div/text()'
        ###########################################################################################################
        #some elements IDs
        search_button_id = 'butSearchSchoolName'
        #############################################################################################################
        #init a selenium driver to get the page url
        driver = webdriver.Chrome()
        driver.get(response.url)
        #select search all schools then press the search button
        select_search_all = driver.find_element_by_xpath(select_search_all_xpath)
        select_search_all.click()
        search_button = driver.find_element_by_id(search_button_id)
        search_button.click()
        #switch the driver to the frame that contains the search results
        frame_results = driver.find_element_by_xpath(frame_results_xpath)
        driver.switch_to.frame(frame_reference=frame_results)
        #dom var contains html source for the frame
        dom = lxml.html.fromstring(driver.page_source)
        num_schools = len(dom.xpath(num_schools_xpath))
        index = 1
        #iterate on search results
        while index <= num_schools:
            #click on result link
            school_link = driver.find_element_by_xpath(school_link_xpath % str(index))
            school_link.click()
            #switch_to the original page source to extract the data
            driver.switch_to.default_content()
            dom = lxml.html.fromstring(driver.page_source)
            #####################################################################################
            #init item
            school_item = SchoolScrapingItem()
            school_item["school_name"]	= ""
            school_item['street_address'] = ""
            school_item['city'] = "Montréal"
            school_item['province'] = "Québec"
            school_item['postal_code'] = ""
            school_item['phone_number'] = ""
            school_item['school_url'] = ""
            school_item['school_grades'] = ""
            school_item['school_language'] = "French"
            school_item['school_type'] = ""
            school_item['school_board'] = "Commission scolaire de Montréal"
            school_item["response_url"] = response.url
            ######################################################################################
            #extract required data
            school_item["school_name"]	= dom.xpath(school_name_xpath)[0]
            school_item['street_address'] = dom.xpath(street_address_xpath)[0]
            school_item['postal_code'] = " ".join(dom.xpath(postal_code_xpath)[0].split()[-2:])
            school_item['phone_number'] = dom.xpath(phone_number_xpath)[0]
            if len(dom.xpath(school_url_xpath)) > 0:
                school_item['school_url'] = dom.xpath(school_url_xpath)[0]
            school_item['school_type'] = dom.xpath(school_type_xpath)[0]
            if "primaire" in school_item["school_type"]:
                school_item['school_grades'] = "primaire"
            elif "secondaire" in school_item["school_type"]:
                school_item['school_grades'] = "secondaire"
            yield school_item
            ######################################################################################
            #switch back to the frame to fetch the next search result
            driver.switch_to.frame(frame_reference=frame_results)
            index += 1

        driver.close()
