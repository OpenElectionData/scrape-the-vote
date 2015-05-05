#!/usr/bin/python
# -*- coding: utf-8 -*-

import scrapelib
import lxml.html
import os


class Scraper(scrapelib.Scraper):
    def __init__(   self,
                    raise_errors=True,
                    requests_per_minute=30,
                    follow_robots=True,
                    retry_attempts=3,
                    retry_wait_seconds=2,
                    header_func=None,
                    url_pattern=None,
                    string_on_page=None ):

        super(Scraper, self).__init__(  raise_errors=raise_errors,
                                                requests_per_minute=requests_per_minute,
                                                retry_attempts=retry_attempts,
                                                retry_wait_seconds=retry_wait_seconds,
                                                header_func=header_func )
        self.base_url = "http://www.cec.md"
        self.election_id = 2

    
    def crawl(self):
        img_metadata = {
            'timestamp-server': '',
            'timestamp-local': '',
            'election_id': str(self.election_id)
        }

        start_url = self.base_url+"/index.php?pag=news&id=1494&l=ro"
        r = self.get(start_url)
        
        tree = lxml.html.fromstring(r.text)
        city_names = tree.xpath("//div[@class='news_title']//a/text()")
        city_urls = tree.xpath("//div[@class='news_title']//a/@href")

        for city_name, city_url in zip(city_names, city_urls):
            print "CITY:     ", city_name
            if city_url[0] != '/':
                city_url = '/'+city_url
            r = self.get(self.base_url+city_url)
            tree = lxml.html.fromstring(r.text)

            sector_names = tree.xpath("//div[@id='print_div']//div[@class='text_content']//a/text()")
            img_urls = tree.xpath("//div[@id='print_div']//div[@class='text_content']//a/@href")
            for sector_name, img_url in zip(sector_names, img_urls):
                print "SECTOR:   ", sector_name
                img_url = self.base_url+img_url
                img_metadata['hierarchy'] = '/'+city_name.encode('utf-8')+'/'+sector_name.encode('utf-8')

                yield (img_url, img_metadata, None)

            if not sector_names:
                img_url = self.base_url+tree.xpath("//div[@id='print_div']//a/@href")[0]
                img_metadata['hierarchy'] = '/'+city_name.encode('utf-8')

                yield (img_url, img_metadata, None)

