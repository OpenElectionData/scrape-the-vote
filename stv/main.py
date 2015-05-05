#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import absolute_import
from argparse import ArgumentParser
import os
import shutil
import fileinput
from documentcloud import DocumentCloud
from .config import DC_USER, DC_PW


def dispatch():

    parser = ArgumentParser(description="")
    parser_subparsers = parser.add_subparsers()
    sub_init = parser_subparsers.add_parser('init')
    sub_scrape = parser_subparsers.add_parser('scrape')

    sub_init.add_argument(dest='scrapername', help='the name of the scraper to initialize')
    sub_init.set_defaults(func=init)

    sub_scrape.add_argument(dest='scrapername', help='the name of the scraper to run')
    sub_scrape.set_defaults(func=scrape)

    args = parser.parse_args()
    args.func(args)


def init(args) :
    if args.scrapername:
        print('init', args.scrapername)
    else:
        print('Please specify a scraper name')

def scrape(args) :
    dc_project = 'ndi'
    img_dir = 'images/'

    client = DocumentCloud(DC_USER, DC_PW)
    project, created = client.projects.get_or_create_by_title(dc_project)

    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    if args.scrapername:
        module = __import__('stv.%s' % args.scrapername, globals(), locals(), ['Scraper'])
        scraper = getattr(module, 'Scraper')()
        images = scraper.crawl()

        for image in images:
            print("url: %s" %image[0])
            head, tail = os.path.split(image[0])
            if os.path.exists(img_dir+tail):
                print("%s already exists" %tail)
            else:
                if not image[2]: # no post data required
                    r = scraper.get(image[0], stream=True)
                    with open(img_dir+tail, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=1024):
                            f.write(chunk)
                            f.flush()
                else: # post data required
                    r = scraper.post(image[0], data=image[2])
                    # handle this case

                metadata = image[1]
                metadata['timestamp-server'] = r.headers['last-modified'] if 'last-modified' in r.headers else ''
                metadata['timestamp-local'] = r.headers['date'] if 'date' in r.headers else ''
                
                # sqlite stuff here
                
                obj = client.documents.upload(img_dir+tail, project=str(project.id), data=metadata)
                
                #delete image here

    else:
        print('Please specify a scraper name')
