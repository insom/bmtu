#!/usr/bin/env python

import sys
import rfc822
import time
import json
from sqlite3 import connect
from urllib import urlopen, urlencode

c = None
screen_name = None

def fetch():
    going_up = True
    while going_up:
        cu = c.cursor()
        cu.execute('SELECT MAX(tweet_id) max_id FROM tweet')
        results = cu.fetchone()
        tweet_count = None
        if not results[0]:
            print >>sys.stderr, 'No existing tweets found: requesting default timeline.'
            tweet_count = load_tweets()
        else:
            print >>sys.stderr, 'Requesting tweets newer than %lu' % results[0]
            tweet_count = load_tweets(since_id=results[0])
        if not tweet_count:
            going_up = False
    going_down = True
    while going_down:
        cu = c.cursor()
        cu.execute('SELECT MIN(tweet_id) min_id FROM tweet')
        results = cu.fetchone()
        print >>sys.stderr, 'Requesting tweets older than %lu' % results[0]
        tweet_count = load_tweets(max_id=(results[0]-1))
        # The -1 is lame, but max_id is "<=" not just "<"
        if not tweet_count:
            going_down = False

def load_tweets(**kwargs):
    args = dict(count=20, trim_user=1, screen_name=screen_name)
    args.update(**kwargs)
    url = 'http://twitter.com/statuses/user_timeline.json?' + urlencode(args)
    url_ = urlopen(url)
    tweets = json.load(url_)
    for twit in tweets:
        c.execute('INSERT INTO tweet (tweet_id, created, text, source) VALUES (?, ?, ?, ?)',
            (twit['id'],
            time.mktime(rfc822.parsedate(twit['created_at'])),
            twit['text'],
            twit['source']))
    c.commit()
    return len(tweets)

def print_help(args):
    print >>sys.stderr, '''
Usage:

    %s <operation> <username>

Operations:

    * init: Create an initial <username>.db file.
    * fetch: Fill in missing tweets for <username>.db
''' % args[0]

def main(*args):
    global c, screen_name
    if len(args) != 3:
        print_help(args)
    elif args[1] == 'init':
        screen_name = args[2]
        try:
            c = connect('%s.db' % screen_name)
            c.execute('CREATE TABLE tweet (tweet_id INTEGER PRIMARY KEY NOT NULL, created INTEGER NOT NULL, text TEXT NOT NULL, source TEXT)')
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
            fetch()
        except Exception, e:
            print >>sys.stderr, "Error: There was a problem retrieving %s's timeline: %s" % (screen_name, str(e))
            print >>sys.stderr, "Error: This may be a temporary failure, wait a bit and try again."
            sys.exit(-3)
    else:
        print_help(args)

if __name__ == '__main__':
    main(*sys.argv)
