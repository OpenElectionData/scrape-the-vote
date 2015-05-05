#!/usr/bin/python
# -*- coding: utf-8 -*-

import scrapelib
from bs4 import BeautifulSoup
import os


class Scraper(scrapelib.Scraper):
    def __init__(   self,
                    raise_errors=True,
                    requests_per_minute=30,
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
        self.base_url = "http://siede.tse.hn"
        self.election_id = 1


    def crawl(self):
        start_url = self.base_url+"/app.php/divulgacionmonitoreo/reporte-presidente-departamentos"
        departments = self._get_links(start_url)
        for dept_name, dept_url  in departments:
            print "DEPARTMENT:    ", dept_name
            municipalities = self._get_links(self.base_url+dept_url)
            for muni_name, muni_url in municipalities:
                print "MUNICIPALITY:  ", muni_name
                polls = self._get_links(self.base_url+muni_url)
                for poll_name, poll_url in polls:
                    print "POLL:          ", poll_name
                    results = self._get_links(self.base_url+poll_url)
                    for result_name, result_url in results:
                        r = self.get(self.base_url+result_url)
                        soup = BeautifulSoup(r.text)
                        img_url = self.base_url+soup.find('img')["src"]
                        img_info = {'department':dept_name,
                                   'municipality':muni_name,
                                   'poll': poll_name,
                                   'result': result_name,
                                   'timestamp-server': '',
                                   'timestamp-local': '',
                                   'election_id': str(self.election_id)
                                   }

                        yield (img_url, img_info, None)

    def _get_links(self, url):
        r = self.get(url)
        soup = BeautifulSoup(r.text)
        tbl_links = soup.find("table").findAll("a")
        links = [ [link.text, link.attrs['href']] for link in tbl_links ]
        return links
