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
        self.img_dir ='moldova_election/images/'

    
    def scrape(self):
        print "RUNNING MOLDOVA SCRAPER"
        print "-"*30
        
        if not os.path.exists(self.img_dir):
            os.makedirs(self.img_dir)

        images = self.crawl()
        for image in images:
            print image[0]

            head, tail = os.path.split(image[0])
            if os.path.exists(self.img_dir+tail):
                print tail, "already exists"
            else:
                r = self.get(image[0], stream=True)
                with open(self.img_dir+tail, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        f.write(chunk)
                        f.flush()
                metadata = image[1]
                metadata['timestamp-server'] = r.headers['last-modified'] if 'last-modified' in r.headers else ''
                metadata['timestamp-local'] = r.headers['date'] if 'date' in r.headers else ''
                metadata['election_id'] = str(self.election_id)
                yield self.img_dir+tail, metadata
    
    def crawl(self):
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
                img_info = {
                    'municipality': city_name.encode('utf-8'),
                    'sector': sector_name.encode('utf-8')
                }
                yield (img_url, img_info, None)

            if not sector_names:
                img_url = self.base_url+tree.xpath("//div[@id='print_div']//a/@href")[0]
                img_info = {
                    'municipality': city_name.encode('utf-8'),
                    'sector': ''
                }
                yield (img_url, img_info, None)

