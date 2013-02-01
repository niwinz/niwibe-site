---
layout: post.html
title: Project - django-logstream
tags: [python, django]
---

Logging of python is great and the intagracion of django with python logging, it is also very good. But sometimes we have to run multiple instances (processes) and want to save the logs without having problems with files opened by multiple processes.

'django-logstream' solves this problem. It runs as a service (separate process) that receives logs of different instances, this allowing multiple processes to the log stored in one file without any problem.

Currently, 'django-logstream' uses ZeroMQ for interprocess communication and now with encrypted data transfer!

**Documentation:** <http://readthedocs.org/docs/django-logstream/en/latest/>

**Download**: <http://pypi.python.org/pypi/django-logstream/>


### Features: ###

* alias for receive multiple streams (multiple handlers)
* interval logrotate mechanism
* secure mode with **blowfish** encription and **sha** checksum

### TODO: ###

* size logrotate mechanism
