#!/usr/bin/python
# -*- coding: utf-8 -*-

import scrapelib
import lxml.html
import os
import urllib
import json

class Scraper(scrapelib.Scraper):
    def __init__(   self,
                    raise_errors=True,
                    requests_per_minute=60,
                    follow_robots=True,
                    retry_attempts=3,
                    retry_wait_seconds=5,
                    header_func=None,
                    url_pattern=None,
                    string_on_page=None ):

        super(Scraper, self).__init__(  raise_errors=raise_errors,
                                                requests_per_minute=requests_per_minute,
                                                retry_attempts=retry_attempts,
                                                retry_wait_seconds=retry_wait_seconds,
                                                header_func=header_func )
        
        self.base_url = "http://www.isie.tn"
        self.election_id = 4
        self.dc_project = 'Tunisia Presidential'
     
    def findImages(self, cat_ids):
        another_blob = None
        try:
            for cat_id in iter(cat_ids):
                self.js_payload['root'] = 'wpfb-cat-%s' % cat_id
                _, another_blob = self.urlretrieve(self.post_back, 
                                                   method='POST', 
                                                   body=urllib.urlencode(self.js_payload))
                
                more_ids = [c['cat_id'] for c in another_blob.json()]
                
                for image in self.findImages(more_ids):
                    yield image

        except (TypeError, KeyError) as e:
            # yield another_blob
            another_blob = json.loads(another_blob.content.decode('utf-8'))
            images = [c['text'] for c in another_blob]
            for image in images:
                yield image
        

    def crawl(self):
        
        img_metadata = {
            'timestamp-server': '',
            'timestamp-local': '',
            'election_id': str(self.election_id)
        }

        start_url = '{0}/ar/%D8%A7%D9%84%D9%86%D8%AA%D8%A7%D8%A6%D8%AC/%D9%86%D8%AA%D8%A7%D8%A6%D8%AC-%D8%A7%D9%84%D8%A7%D9%86%D8%AA%D8%AE%D8%A7%D8%A8%D8%A7%D8%AA-%D8%A7%D9%84%D8%B1%D8%A6%D8%A7%D8%B3%D9%8A%D8%A9/'.format(self.base_url)
        
        _, entry = self.urlretrieve(start_url)
        
        self.post_back = 'http://www.isie.tn/wp-content/plugins/wp-filebase/wpfb-ajax.php'
        
        self.headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        self.headers['Accept-Encoding'] = 'en-US;q=0.5'
        self.headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
        
        self.js_payload = {
            'root': 'wpfb-cat-6804',
            'action': 'tree', 
            'type': 'browser', 
            'base': '6425'
        }
        
        _, category_listing = self.urlretrieve(self.post_back, 
                                               method="POST", 
                                               body=urllib.urlencode(self.js_payload))
        
        cat_ids = [c['cat_id'] for c in category_listing.json()]

        for image in self.findImages(cat_ids):
            # yield image
            image = lxml.html.fromstring(image)
            link = image.xpath('//a/@href')[0]
            img_metadata['hierarchy'] = urllib.unquote(link.split('Tunisie')[1])\
                                               .rsplit('/', 1)[0]
            yield (link, img_metadata, None)
            
