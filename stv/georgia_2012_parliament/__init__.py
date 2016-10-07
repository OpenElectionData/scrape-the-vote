#!/usr/bin/python
# -*- coding: utf-8 -*-

import scrapelib
import lxml.html
import os


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
        
        self.base_url = "http://results2012.cec.gov.ge"
        self.election_id = 5
        self.dc_project = 'Georgia 2012 Parliament'
     
    def _lxmlize(self, url, payload=None):

        _, entry = self.urlretrieve(url)
        
        page = lxml.html.fromstring(entry.content)
        page.make_links_absolute(url)
        return page
    
    def crawl(self):
        img_metadata = {
            'timestamp-server': '',
            'timestamp-local': '',
            'election_id': str(self.election_id)
        }

        root_tree = self._lxmlize(self.base_url)
        
        meri_names = root_tree.xpath("//table[@id='table36']//a/text()")
        meri_urls = root_tree.xpath("//table[@id='table36']//a/@href")

        for meri_name, oqmi_url in zip(meri_names, meri_urls):
            if oqmi_url != self.base_url:
                meri_name = meri_name.split(' ', 1)[1]
                
                oqmi_tree = self._lxmlize(oqmi_url)
                cells = oqmi_tree.xpath("//td[@bgcolor='#EFEFEF']")
                
                for cell in cells:
                    
                    if cell.find('a') is not None:
                        image_link = cell.find('a')
                        image_page_url = image_link.attrib['href']
                        oqmi_number = image_page_url.rsplit('_', 1)[1].split('.')[0]
                        
                        # Get proportional results 
                        image_page = self._lxmlize(image_page_url)
                        image_url = image_page.xpath('//img/@src')[0]

                        img_metadata['hierarchy'] = u'/proportional/%s/%s' % (meri_name, oqmi_number)
                        
                        yield (image_url, img_metadata, None)
                        
                        # Get majoritarian results 
                        image_page_url = image_page_url.replace('prop', 'major')

                        image_page = self._lxmlize(image_page_url)
                        image_url = image_page.xpath('//img/@src')[0]

                        img_metadata['hierarchy'] = u'/majoritarian/%s/%s' % (meri_name, oqmi_number)
                        
                        yield (image_url, img_metadata, None)
