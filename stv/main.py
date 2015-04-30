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
    sub_urlgrab = parser_subparsers.add_parser('urlgrab')
    sub_process = parser_subparsers.add_parser('process')
    sub_upload = parser_subparsers.add_parser('upload')

    sub_init.add_argument(dest='scrapername', help='the name of the scraper to initialize')
    sub_init.set_defaults(func=init)

    sub_urlgrab.add_argument(dest='scrapername', help='the name of the scraper to run')
    sub_urlgrab.set_defaults(func=urlgrab)

    sub_process.add_argument(dest='electionid', help='the election id')
    sub_process.set_defaults(func=process)

    sub_upload.add_argument(dest='electionid', help='the election id')
    sub_upload.set_defaults(func=upload)

    args = parser.parse_args()
    args.func(args)


def init(args) :
    if args.scrapername:
        print('init', args.scrapername)
    else:
        print('Please specify a scraper name')

def urlgrab(args) :
    if args.scrapername:
        module = __import__('stv.%s' % args.scrapername, globals(), locals(), ['Scraper'])
        scraper = getattr(module, 'Scraper')()
        scraper.scrape()
    else:
        print('Please specify a scraper name')

def process(args) :
    if args.electionid:
        print('process', args.electionid)
    else:
        print('Please specify an election id')

def upload(args) :
    if args.electionid:
        print('upload', args.electionid)
    else:
        print('Please specify an election id')
