#!/usr/bin/env python

import sys
import rfc822
import time
import json
from sqlite3 import connect, IntegrityError
from urllib import urlencode
import requests

c = None
screen_name = None

def fetch():
    offset = 0
    results = 1
    while results > 0:
        results = load_posts(offset)
        offset += results
    return offset

def load_posts(offset=0):
    url_ = requests.get('http://api.tumblr.com/v2/blog/%s.tumblr.com/posts?api_key=PyezS3Q4Smivb24d9SzZGYSuhMNPQUhMsVetMC9ksuGPkK1BTt&filter=raw&offset=%d' % (screen_name, offset))
    posts = url_.json['response']['posts']
    added_posts = 0
    for post in posts:
        date, tz = post['date'].rsplit(' ', 1)
        ts = time.mktime(time.strptime(date, '%Y-%m-%d %H:%M:%S'))
        try:
            c.execute('INSERT INTO post (post_id, created, json) VALUES (?, ?, ?)',
                (post['id'],
                ts,
                json.dumps(post)))
        except IntegrityError, e:
            # We've hit duplicate posts
            break
        added_posts += 1
    c.commit()
    return added_posts

def print_help(args):
    print >>sys.stderr, '''
Usage:

    %s <operation> <username>

Operations:

    * init: Create an initial <username>.db file.
    * fetch: Fill in missing posts for <username>.db
''' % args[0]

def main(*args):
    global c, screen_name
    if len(args) != 3:
        print_help(args)
    elif args[1] == 'init':
        screen_name = args[2]
        try:
            c = connect('%s.db' % screen_name)
            c.execute('CREATE TABLE post (post_id INTEGER PRIMARY KEY NOT NULL, created INTEGER NOT NULL, json TEXT NOT NULL)')
        except Exception, e:
            print >>sys.stderr, "Error: There was a problem creating your database: %s" % str(e)
            sys.exit(-1)
    elif args[1] == 'fetch':
        screen_name = args[2]
        try:
            c = connect('%s.db' % screen_name)
        except Exception, e:
            print >>sys.stderr, "Error: There was a problem opening your database: %s" % str(e)
            sys.exit(-2)
        try:
            count = fetch()
            print >>sys.stderr, "Imported %d posts." % count
        except Exception, e:
            print >>sys.stderr, "Error: There was a problem retrieving %s's timeline: %s" % (screen_name, str(e))
            print >>sys.stderr, "Error: This may be a temporary failure, wait a bit and try again."
            sys.exit(-3)
    else:
        print_help(args)

if __name__ == '__main__':
    main(*sys.argv)
