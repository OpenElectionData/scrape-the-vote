#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import absolute_import
from argparse import ArgumentParser
import os
import shutil
import fileinput


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
    if args.scrapername:
        module = __import__('stv.%s' % args.scrapername, globals(), locals(), ['Scraper'])
        scraper = getattr(module, 'Scraper')()
        scraper.scrape()
    else:
        print('Please specify a scraper name')
