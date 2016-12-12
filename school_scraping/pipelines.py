# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import csv
import os.path
import platform

class SchoolScrapingPipeline(object):
    def process_item(self, school_item, spider):
        page_url = school_item["response_url"]
        name = school_item["school_name"]
        street_address = school_item['street_address']
        city = school_item['city']
        province = school_item['province']
        postal_code = school_item['postal_code']
        phone_number = school_item['phone_number']
        school_website_url = school_item['school_url']
        grades = school_item['school_grades']
        language = school_item['school_language']
        school_type = school_item['school_type']
        school_board = school_item['school_board']
        if page_url is None:
            page_url = ""
        if name is None:
            name = ""
        if street_address is None:
            street_address = ""
        if city is None:
            city = ""
        if province is None:
            province = ""
        if postal_code is None:
            postal_code = ""
        if phone_number is None:
            phone_number = ""
        if school_website_url is None:
            school_website_url = ""
        if grades is None:
            grades = ""
        if language is None:
            language = ""
        if school_type is None:
            school_type = ""
        if school_board is None:
            school_board = ""

        path_seperator = "/"
        if platform.system() == 'Windows':
            path_seperator = "\\"
        mode = 'wb'
        file_name = "output_data.csv"
        file_path = path_seperator.join(os.path.abspath(os.path.dirname(__file__)).split(path_seperator)[:-1]) + path_seperator + file_name
        if os.path.isfile(file_path):
            mode = 'ab'
        with open(file_name, mode) as csvfile:
            fieldnames = [
                'page_url',
                'name',
                'street_address',
                'city',
                'province',
                'postal_code',
                'phone_number',
                'school_website_url',
                'grades',
                'language',
                'school_type',
                'school_board'
            ]
            writer = csv.DictWriter(csvfile, delimiter=';', fieldnames=fieldnames)
            if mode == 'wb':
                writer.writeheader()
            writer.writerow(
                {
                    'page_url':unicode(page_url).encode('utf-8'),
                    'name':unicode(name).encode('utf-8'),
                    'street_address':unicode(street_address).encode('utf-8'),
                    'city':unicode(city).encode('utf-8'),
                    'province':unicode(province).encode('utf-8'),
                    'postal_code':unicode(postal_code).encode('utf-8'),
                    'phone_number':unicode(phone_number).encode('utf-8'),
                    'school_website_url':unicode(school_website_url).encode('utf-8'),
                    'grades':unicode(grades).encode('utf-8'),
                    'language':unicode(language).encode('utf-8'),
                    'school_type':unicode(school_type).encode('utf-8'),
                    'school_board':unicode(school_board).encode('utf-8')
                }
            )

        return school_item
