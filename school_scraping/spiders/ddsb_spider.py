# -*- coding: utf-8 -*-
import scrapy
from ..items import SchoolScrapingItem
from w3lib.html import remove_tags


class DdsbSpiderSpider(scrapy.Spider):
    name = "ddsb_spider"
    allowed_domains = ["ddsb.ca"]
    start_urls = (
        'http://ddsb.ca/Schools/Pages/default.aspx',
    )

    def parse(self, response):
        ###########################################################################################
        #some useful xpath variables
        elementary_Schools_xpath = '//*[@id="sl-ElementarySchoolSelect"]/option/@value'
        secondary_Schools_xpath = '//*[@id="sl-SecondarySchoolSelect"]/option/@value'
        #############################################################################
        meta_elementary = {"type":"Elementary School", "grades" : "(K - Grade 8)"}
        meta_secondary = {"type":"Secondary School", "grades" : "(Grade 9 - Grade 12)"}
        #########################################################################
        elementary_Schools = response.xpath(elementary_Schools_xpath).extract()
        secondary_Schools = response.xpath(secondary_Schools_xpath).extract()
        #####################################################################
        for url in elementary_Schools:
            if url != '':
                yield scrapy.Request(response.urljoin(url), callback=self.parse_school_profile, meta=meta_elementary)
        #####################################################################
        for url in secondary_Schools:
            if url != '':
                yield scrapy.Request(response.urljoin(url), callback=self.parse_school_profile, meta=meta_secondary)

    def digits_only(self, mystring):
        """
        it takes a sting conains some digits then return the only digits
        """
        result = ""
        for ch in mystring:
            if ch.isdigit() or ch == '-':
                result += ch
        return result

    def parse_school_profile(self, response):
        school_name_xpath = '//*[@id="DeltaPlaceHolderPageTitleInTitleArea"]/div/text()'
        school_url_xpath = '//a[@title="School Website"]/@href'
        data1_xpath = '//*[@id="WebPartWPQ3"]/div[1]'
        data2_xpath = '//*[@id="WebPartWPQ2"]/div[1]'
        ####################################################################################
        #init item
        school_item = SchoolScrapingItem()
        school_item["school_name"]	= ''
        school_item['street_address'] = ''
        school_item['city'] = ""
        school_item['province'] = "Ontario"
        school_item['postal_code'] = ""
        school_item['phone_number'] = ""
        school_item['school_url'] = ""
        school_item['school_grades'] = response.meta["grades"]
        school_item['school_language'] = ""
        school_item['school_type'] = response.meta["type"]
        school_item['school_board'] = "Durham District School Board"
        school_item["response_url"] = response.url
        ##########################################################################################################
        school_item["school_name"]	= response.xpath(school_name_xpath).extract_first()
        school_item['school_url'] = response.urljoin(response.xpath(school_url_xpath).extract_first())

        data = remove_tags(response.xpath(data1_xpath).extract_first()).strip()
        if data == '':
            data = remove_tags(response.xpath(data2_xpath).extract_first()).strip()

        ###########################################################################################################
        # data1 = data.split('\n')[0]
        # data1 = data1.replace('Ontario', '')
        tmp_addr = data.split(',')[0]
        i = 0
        for ch in tmp_addr:
            if ch.isdigit():
                i = tmp_addr.index(ch)
                break

        school_item['street_address'] = ''.join(tmp_addr[i:])
        if 'Ontario' in data:
            school_item['postal_code'] = data[data.index('Ontario') + 7:data.index('Ontario') + 14]
        school_item['city'] = data.split(',')[1]
        if len(data.split(',')[1]) > 30:
            import re
            school_item['city'] = re.findall('[A-Z][^A-Z]*', data.split(',')[0].split()[-1])[-1]
        # if len(data1.split(',')) == 3:
        #     school_item['city'] = data1.split(',')[2]
        # else:
        #     school_item['city'] = school_item['street_address'].split()[-1]
        ########################################################################################################
        school_item['phone_number'] = self.digits_only(data[data.index('p:'):data.index('p:') + 15])
        yield school_item
