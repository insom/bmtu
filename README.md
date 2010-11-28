Back My Twits Up
================

bmtu.py is a very, very simple Twitter backup tool. Most tools that I found
online either did a lot of things and pulled in many dependencies (Tweetnest),
basically didn't handle errors at all (most shell and Python recipies), or
weren't designed for running more than once.

bmtu.py only depends on Python and libraries that ship with Ubuntu's python
package. It requires Python 2.6 or above, and SQLite3. It handles most errors
by giving up, and uses transactions to handle errors without corruption.

On performing a fetch, it checks for tweets newer and older than what is stored
in the database. It will only pull in 20 new tweets, so it should be run from a
cron. Way up there on the TODO list is performing pagination on importing new
tweets.

Currently bmtu.py will use two unauthenticated API calls per hour doing
nothing, and an additional call per block of 20 tweets downloaded.

The Quick Start
---------------

# Create a database.

$ python bmtu.py init insom

# Perform the initial import.

$ python bmtu.py fetch insom

# Add to an hourly cron.

0 * * * * python bmtu.py fetch insom

License
-------

Copyright (c) 2010, Aaron Brady

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
