#!/usr/bin/env python

import sys
import rfc822
import time
import json
import iso8601
from sqlite3 import connect
from urllib import urlopen, urlencode

c = None
uid = None

def fetch():
    going_up = True
    while going_up:
        cu = c.cursor()
        cu.execute('SELECT MAX(post_id) max_id FROM post')
        results = cu.fetchone()
        post_count = None
        if not results[0]:
            print >>sys.stderr, 'No existing posts found: requesting default timeline.'
            post_count = load_posts()
        else:
            print >>sys.stderr, 'Requesting posts newer than %lu' % results[0]
            post_count = load_posts(since_id=results[0])
        if not post_count:
            going_up = False
    going_down = True
    while going_down:
        cu = c.cursor()
        cu.execute('SELECT MIN(post_id) min_id FROM post')
        results = cu.fetchone()
        print >>sys.stderr, 'Requesting posts older than %lu' % results[0]
        post_count = load_posts(before_id=(results[0]))
        if not post_count:
            going_down = False

def load_posts(**kwargs):
    args = dict(count=200)
    args.update(**kwargs)
    url = ('https://alpha-api.app.net/stream/0/users/%s/posts?' % uid) + urlencode(args)
    url_ = urlopen(url)
    posts = json.load(url_)
    if type(posts) == dict and posts['meta'].has_key('error_message'):
        raise Exception(posts['meta']['error_message'])
    for twit in posts['data']:
        c.execute('INSERT INTO post (post_id, created, text, source) VALUES (?, ?, ?, ?)',
            (twit['id'],
            iso8601.parse_date(twit['created_at']),
            twit['text'],
            twit['source']['name']))
    c.commit()
    return len(posts['data'])

def print_help(args):
    print >>sys.stderr, '''
Usage:

    %s <operation> <username>

Operations:

    * init: Create an initial <username>.db file.
    * fetch: Fill in missing posts for <username>.db
''' % args[0]

def main(*args):
    global c, uid
    if len(args) != 3:
        print_help(args)
    elif args[1] == 'init':
        uid = args[2]
        try:
            c = connect('%s.db' % uid)
            c.execute('CREATE TABLE post (post_id INTEGER PRIMARY KEY NOT NULL, created INTEGER NOT NULL, text TEXT NOT NULL, source TEXT)')
        except Exception, e:
            print >>sys.stderr, "Error: There was a problem creating your database: %s" % str(e)
            sys.exit(-1)
    elif args[1] == 'fetch':
        uid = args[2]
        try:
            c = connect('%s.db' % uid)
        except Exception, e:
            print >>sys.stderr, "Error: There was a problem opening your database: %s" % str(e)
            sys.exit(-2)
        try:
            fetch()
        except Exception, e:
            print >>sys.stderr, "Error: There was a problem retrieving %s's timeline: %s" % (uid, str(e))
            print >>sys.stderr, "Error: This may be a temporary failure, wait a bit and try again."
            sys.exit(-3)
    else:
        print_help(args)

if __name__ == '__main__':
    main(*sys.argv)
