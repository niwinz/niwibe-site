#!/usr/bin/env python
# -*- coding: utf-8 -*- #

AUTHOR = u'Andrey Antukh'
SITENAME = u'Niwi.Be'
SITEURL = 'http://www.niwi.be'

TIMEZONE = 'Europe/Paris'

DEFAULT_LANG = u'en'

# Blogroll
LINKS =  (('Pelican', 'http://docs.notmyidea.org/alexis/pelican/'),
          ('Python.org', 'http://python.org'),
          ('Jinja2', 'http://jinja.pocoo.org'),
          ('You can modify those links in your config file', '#'),)

# Social widget
SOCIAL = (('You can add links in your config file', '#'),
          ('Another social link', '#'),)

DEFAULT_PAGINATION = 12

MENUITEMS = (
    ('videos', '/video-archives.html'),
)

GITHUB = 'https://github.com/niwibe'

DISPLAY_PAGES_ON_MENU = True
REVERSE_CATEGORY_ORDER = True

FILES_TO_COPY = (('extra/robots.txt', 'robots.txt'),)

THEME = "themes/niwibe"

FEED_ALL_RSS = 'feeds/all.rss.xml'
CATEGORY_FEED_RSS = 'feeds/%s.rss.xml'
FILENAME_METADATA = '(?P<date>\d{4}-\d{2}-\d{2})-(?P<slug>.+)'

ARTICLE_URL = '{date:%Y}/{date:%m}/{date:%d}/{slug}/'
ARTICLE_SAVE_AS = '{date:%Y}/{date:%m}/{date:%d}/{slug}/index.html'

#STATIC_PATHS = ["pictures", ]
TEMPLATE_PAGES = {'pages/about.html': 'about.html'}

PROJECTS = [
    ('django-redis', 'https://github.com/niwibe/django-redis',
        u'Full featured redis cache backend for Django.'),
    ('django-jinja', 'https://github.com/niwibe/django-jinja',
        u'Jinja2 templating language integrated in Django.'),
    ('py-couchdb', 'https://github.com/niwibe/py-couchdb',
        u'Modern pure python CouchDB Client.'),
    ('wand', 'https://github.com/dahlia/wand',
        u'The ctypes-based simple ImageMagick binding for Python'),
    ('django-ext-pool', 'https://github.com/niwibe/djorm-ext-pool',
        u'DB-API2 connection pool for Django'),
    ('django-ext-pgarray', 'https://github.com/niwibe/djorm-ext-pgarray',
        u'PostgreSQL native array fields extension for Django'),
    ('django-ext-hstore', 'https://github.com/niwibe/djorm-ext-hstore',
        u'PostgreSQL HStore module integraion for Django'),
    ('py-mhash', 'https://github.com/niwibe/py-mhash',
        'Mhash ctypes bindings for python3 and python2'),
    ('moment-tokens', 'https://github.com/niwibe/moment-tokens',
        u'Unix (strftime) and php format translations for momentjs'),
    ('django-sse', 'https://github.com/niwibe/django-sse',
        u'HTML5 Server-Sent Events integration for Django'),
    ('sse', 'https://github.com/niwibe/sse',
        'Server Sent Events protocol implemetation on python2/3'),
]
