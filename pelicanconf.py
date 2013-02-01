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

DEFAULT_PAGINATION = 14

MENUITEMS = (
    ('videos', '/video-archives.html'),
)

DISPLAY_PAGES_ON_MENU = True
REVERSE_CATEGORY_ORDER = True

FILES_TO_COPY = (('extra/robots.txt', 'robots.txt'),)

GOOGLE_ANALYTICS = u"UA-23352570-2"
DISQUS_SITENAME = "niwibe"
THEME = "themes/niwibe"


FEED_ALL_RSS = 'feeds/all.rss.xml'
CATEGORY_FEED_RSS = 'feeds/%s.rss.xml'
FILENAME_METADATA = '(?P<date>\d{4}-\d{2}-\d{2})-(?P<slug>.+)'

ARTICLE_URL = '{date:%Y}/{date:%m}/{date:%d}/{slug}/'
ARTICLE_SAVE_AS = '{date:%Y}/{date:%m}/{date:%d}/{slug}/index.html'

#STATIC_PATHS = ["pictures", ]
TEMPLATE_PAGES = {'pages/about.html': 'about.html'}
