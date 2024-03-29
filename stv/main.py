#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import absolute_import
from argparse import ArgumentParser
import os
import shutil
import fileinput
from documentcloud import DocumentCloud
from .config import DC_USER, DC_PW, TRANSCRIBER_ENDPOINT
import sqlite3
import hashlib
import subprocess
import time
import requests
import socket
from datetime import datetime

# this is for the 'stv' entry point
def dispatch():

    parser = ArgumentParser(description="")
    parser_subparsers = parser.add_subparsers()
    sub_init = parser_subparsers.add_parser('init', help='creates documents.db and tables to store crawled URLs')
    sub_kickoff_scrape = parser_subparsers.add_parser('dispatch', help='dispatches a scraper (crawling + uploading)')
    sub_testcrawl = parser_subparsers.add_parser('testcrawl', help='only dispatches the crawler in a scraper (skips uploading)')

    sub_init.set_defaults(func=init)

    sub_kickoff_scrape.add_argument(dest='scrapername', help='the name of the scraper to run')
    sub_kickoff_scrape.set_defaults(func=kickoff_scrape)
    sub_kickoff_scrape.add_argument("--retry-attempts", type=int,
                    help="the number of times the scraper should attempt to access a page")
    sub_kickoff_scrape.add_argument("--retry-wait-seconds", type=int,
                    help="the number of seconds to wait before re-trying to access a page")
    sub_kickoff_scrape.add_argument("--requests-per-minute", type=int,
                    help="the number of requests per minute")

    sub_testcrawl.add_argument(dest='scrapername', help='the name of the scraper to run')
    sub_testcrawl.set_defaults(func=testcrawl)
    sub_testcrawl.add_argument("--retry-attempts", type=int,
                    help="the number of times the scraper should attempt to access a page")
    sub_testcrawl.add_argument("--retry-wait-seconds", type=int,
                    help="the number of seconds to wait before re-trying to access a page")
    sub_testcrawl.add_argument("--requests-per-minute", type=int,
                    help="the number of requests per minute")
    sub_testcrawl.add_argument("--image-limit", type=int,
                    help="the number of urls to return (defaults to 5)")

    args = parser.parse_args()
    args.func(args)

# this is for the 'hidden_dispatch' entry point
def hidden_dispatch():

    parser = ArgumentParser(description="")
    parser_subparsers = parser.add_subparsers()
    sub_crawl = parser_subparsers.add_parser('crawl')
    sub_upload = parser_subparsers.add_parser('upload')


    sub_crawl.add_argument(dest='scrapername')
    sub_crawl.set_defaults(func=crawl)
    sub_crawl.add_argument("--retry-attempts", type=int)
    sub_crawl.add_argument("--retry-wait-seconds", type=int)
    sub_crawl.add_argument("--requests-per-minute", type=int)

    sub_upload.add_argument(dest='scrapername')
    sub_upload.set_defaults(func=upload)

    args = parser.parse_args()
    args.func(args)


def init(args) :
    # create documents table if it doesn't exist
    con = sqlite3.connect('documents.db')
    with con:
        cur = con.cursor()
        create_docs_sql = 'CREATE TABLE IF NOT EXISTS documents ('  \
                    'id INTEGER PRIMARY KEY,'               \
                    'election_id INTEGER,'                  \
                    'scraper_name TEXT,'                    \
                    'url TEXT,'                             \
                    'name TEXT,'                            \
                    'file_hash TEXT,'                       \
                    'hierarchy TEXT,'                       \
                    'timestamp_server TEXT,'                \
                    'timestamp_local TEXT'                  \
                    ');'
        create_temp_dump_sql = 'CREATE TABLE IF NOT EXISTS temp_documents ('  \
                    'id INTEGER PRIMARY KEY,'               \
                    'scraper_name TEXT,'                    \
                    'url TEXT,'                             \
                    'hierarchy TEXT,'                       \
                    'post_data TEXT,'                       \
                    'is_seen INTEGER'                      \
                    ');'

        cur.execute(create_docs_sql)
        cur.execute(create_temp_dump_sql)
        con.commit()

def kickoff_scrape(args) :

    if args.scrapername:
        while True:

            extra_args = {}
            if args.retry_attempts:
                extra_args['retry_attempts'] = args.retry_attempts
            if args.retry_wait_seconds:
                extra_args['retry_wait_seconds'] = args.retry_wait_seconds
            if args.requests_per_minute:
                extra_args['requests_per_minute'] = args.requests_per_minute
                        
            procs = [   subprocess.Popen(['hidden_dispatch', 'crawl', args.scrapername]),
                        subprocess.Popen(['hidden_dispatch', 'upload', args.scrapername])  ]
                        
            for proc in procs:
                proc.wait()

    else:
        print('Please specify a scraper name')

def crawl(args) :

    dc_project = 'ndi'  # default document cloud project
    img_dir = 'images/' # the local directory where images will be downloaded

    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    extra_args = {}
    if args.retry_attempts:
        extra_args['retry_attempts'] = args.retry_attempts
    if args.retry_wait_seconds:
        extra_args['retry_wait_seconds'] = args.retry_wait_seconds
    if args.requests_per_minute:
        extra_args['requests_per_minute'] = args.requests_per_minute

    module = __import__('stv.%s' % args.scrapername, globals(), locals(), ['Scraper'])
    scraper = getattr(module, 'Scraper')(**extra_args)
    
    while True:
        images = scraper.crawl()
        
        for image in images:
            con = sqlite3.connect('documents.db')
            
            insert_str = u'INSERT INTO temp_documents \
                           (scraper_name, url, hierarchy, post_data, is_seen) \
                           VALUES (?,?,?,?,?);'
            
            try:
                with con:
                    con.execute(insert_str,(args.scrapername, 
                                            image[0],
                                            image[1]['hierarchy'],
                                            image[2],
                                            False))

            except sqlite3.OperationalError as e:
                time.sleep(1)
                if 'database is locked' in str(e):
                    print(e)
                    i = 0
                    while i < 10:
                        try:
                            with con:
                                con.execute(insert_str,(args.scrapername,
                                                        image[0],
                                                        image[1]['hierarchy'],
                                                        image[2],
                                                        False))
                            break
                        except sqlite3.OperationalError as e:
                            print(e)
                            i += 1
                            continue


def upload(args) :

    dc_project = 'ndi'  # default document cloud project
    img_dir = 'images/' # the local directory where images will be downloaded

    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    module = __import__('stv.%s' % args.scrapername, globals(), locals(), ['Scraper'])
    scraper = getattr(module, 'Scraper')()

    if scraper.dc_project:
        dc_project = scraper.dc_project
    client = DocumentCloud(DC_USER, DC_PW)
    project, created = client.projects.get_or_create_by_title(dc_project)

    if scraper.election_id:
        election_id = scraper.election_id


    while True:
        con = sqlite3.connect('documents.db')
        
        cur = con.cursor()
        image_q = 'SELECT * FROM temp_documents WHERE is_seen=0 AND scraper_name = ?'
        cur.execute(image_q, (args.scrapername,))
        image = cur.fetchone()
        con.close()
        
        if image:
            image_temp_id, scraper_name, url, hierarchy, post_data = image[:5] 
            
            head, tail = os.path.split(url)

            if os.path.exists(img_dir+tail):
                os.remove(img_dir+tail)
            
            print(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), image[1])

            hasher = hashlib.sha1()
            file_hash = ''
            timestamp_server = ''
            timestamp_local = ''
            
            req_kwargs = {}

            if post_data:
                req_kwargs = {'method': 'POST', 'body': post_data}
            with open(img_dir+tail, 'wb') as f:
                try:
                    _, r = scraper.urlretrieve(url.encode('utf-8'), **req_kwargs)
                except (requests.HTTPError, socket.error):
                    i = 0
                    while i < 10:
                        time.sleep(1)
                        try:
                            _, r = scraper.urlretrieve(url, **req_kwargs)
                            break
                        except (requests.HTTPError, socket.error):
                            i += 1
                            print('retrying %s' % url)
                            continue
                f.write(r.content)
                hasher.update(r.content)
            file_hash = hasher.hexdigest()
            timestamp_server = r.headers['last-modified'] if 'last-modified' in r.headers else ''
            timestamp_local = r.headers['date'] if 'date' in r.headers else ''
            
            # adding image to documents table
            con = sqlite3.connect('documents.db')
            
            insert_str = 'INSERT INTO documents \
                        (election_id,url,name,file_hash,hierarchy,timestamp_server,timestamp_local) \
                        VALUES (?,?,?,?,?,?,?);'
            q_update = 'SELECT * FROM documents where url=? and file_hash!=? and file_hash!=""'
            q_duplicate = 'SELECT * FROM documents where url=? and file_hash=?'
            q_mark_seen = 'UPDATE temp_documents SET is_seen=? where id=?'

            cur = con.cursor()
            cur.execute(q_mark_seen,(1, image_temp_id))
            cur.execute(q_update,(url,file_hash))
            is_update = cur.fetchone()
            cur.execute(q_duplicate,(url,file_hash))
            is_duplicate = cur.fetchone()
            cur.execute(insert_str,(election_id,url,tail,file_hash,hierarchy,timestamp_server,timestamp_local))
            con.commit()

            con.close()

            if not is_duplicate:
                # do something here if image is an update of an image we've already seen

                metadata={}
                # uploading image to document cloud
                metadata['hierarchy'] = hierarchy.encode('utf-8')
                metadata['election_id'] = str(election_id)
                metadata['timestamp_local'] = timestamp_local
                metadata['timestamp_server'] = timestamp_server
                obj = client.documents.upload(img_dir+tail, 
                                              access='public', 
                                              project=str(project.id), 
                                              data=metadata)
                
                if TRANSCRIBER_ENDPOINT:
                    payload = {
                        'project_id': project.id, 
                        'project_title': dc_project,
                        'document_id': obj.id
                    }
                    try:
                        r = requests.post(TRANSCRIBER_ENDPOINT, data=payload)
                    except requests.exceptions.ConnectionError:
                        pass

            try:
                os.remove(img_dir+tail)
            except OSError:
                pass
        else:
            time.sleep(1)

def testcrawl(args) :

    extra_args = {}
    if args.retry_attempts:
        extra_args['retry_attempts'] = args.retry_attempts
    if args.retry_wait_seconds:
        extra_args['retry_wait_seconds'] = args.retry_wait_seconds
    if args.requests_per_minute:
        extra_args['requests_per_minute'] = args.requests_per_minute

    module = __import__('stv.%s' % args.scrapername, globals(), locals(), ['Scraper'])
    scraper = getattr(module, 'Scraper')(**extra_args)

    images = scraper.crawl()

    count = 0
    if args.image_limit:
        limit = args.image_limit
    else:
        limit = 5
    for image in images:
        print("\ngrabbed an image!")
        print(image)
        count += 1
        if count == limit:
            print("\ndone testing crawler")
            break

