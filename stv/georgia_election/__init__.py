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
        
        self.base_url = "http://results2014.cec.gov.ge"
        self.election_id = 3
        self.dc_project = 'Georgia Mayoral'
     
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

        tblisi_start_url = '%s/meri_tbilisi.html' % self.base_url
        root_tree = self._lxmlize(tblisi_start_url)
        
        meri_names = root_tree.xpath("//table[@id='table2']//a/text()")
        meri_urls = root_tree.xpath("//table[@id='table2']//a/@href")

        for meri_name, oqmi_url in zip(meri_names, meri_urls):
            if oqmi_url != tblisi_start_url:
                meri_name = meri_name.split(' ', 1)[1]
                
                oqmi_tree = self._lxmlize(oqmi_url)
                cells = oqmi_tree.xpath("//td[@bgcolor='#EFEFEF']")
                
                for cell in cells:
                    
                    if cell.find('a') is not None:
                        image_link = cell.find('a')
                        image_page_url = image_link.attrib['href']
                        oqmi_number = image_page_url.rsplit('_', 1)[1].split('.')[0]
                    
                        image_page = self._lxmlize(image_page_url)
                        image_url = image_page.xpath('//img/@src')[0]

                        img_metadata['hierarchy'] = u'/%s/%s' % (meri_name, oqmi_number)
                        
                        yield (image_url, img_metadata, None)
        
        the_rest_start_url = 'http://results2014.cec.gov.ge/proporciuli.html'
        root_tree = self._lxmlize(the_rest_start_url)

        olq_names = root_tree.xpath("//table[@id='table36']//a/text()")
        olq_urls = root_tree.xpath("//table[@id='table36']//a/@href")

        for olq_name, olq_url in zip(olq_names, olq_urls):
            if olq_url != the_rest_start_url:
                olq_name = olq_name.split(' ', 1)[1]

                olq_tree = self._lxmlize(olq_url)
                cells = olq_tree.xpath("//td[@bgcolor='#EFEFEF']")

                for cell in cells:
                    if cell.find('a') is not None:
                        image_link = cell.find('a')
                        image_page_url = image_link.attrib['href']
                        olq_number = image_page_url.rsplit('_', 1)[1].split('.')[0]
                    
                        image_page = self._lxmlize(image_page_url)
                        image_url = image_page.xpath('//img/@src')[0]

                        img_metadata['hierarchy'] = u'/%s/%s' % (olq_name, olq_number)
                        
                        yield (image_url, img_metadata, None)
