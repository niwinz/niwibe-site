#!/usr/bin/env python
# -*- coding: utf-8 -*- #

import os
import sys
sys.path.append(os.curdir)
from pelicanconf import *

SITEURL = 'http://www.niwi.nz'

FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = 'feeds/%s.atom.xml'


DELETE_OUTPUT_DIRECTORY = True
RELATIVE_URLS = False

GOOGLE_ANALYTICS = "UA-23352570-2"
DISQUS_SITENAME = "niwibe"
