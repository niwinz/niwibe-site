---
layout: post.html
title: Persistent database connections with Django.
tags: [python, django, orm]
---

Those who work with django, we know that it lacks a connection pool. That on some occasions may be an important piece and we always have to look for solutions outside of django, mainly snippets.

On the other hand we have sqlalchemy, which supports persistent connections to the database. But what really interests us is the ability to embed a connection pool to any Connection client database that implements the specification dbapi2.

There are many and different snipperts online that explain how to solve this problem. But they are just "snippets".

The main idea of ``djorm-ext-pool`` is offering a package that enables a simple way to activate a connection pool for the django orm. Obviously using the implementation of sqlalchemy connection pool.

How to install
--------------

Run ``python setup.py install`` to install, or place ``djorm_pool`` on your Python path.

You can also install it with: ``pip install djorm-ext-pool``


How to use it
-------------

Very simple, put ``djorm_pool`` in your ``INSTALLED_APPS`` on your ``settings.py`` as first element if possible:

~~~ { python }
# settings.py

INSTALLED_APPS = (
    'djorm_pool',
    ...
)
~~~

You can add options to sqlalchemy connection pool adding them in the settings ``DJORM_POOL_OPTIONS``.

~~~ { python }
DJORM_POOL_OPTIONS = {
    "pool_size": 20,
    "max_overflow": 0
}
~~~

<br />
#### Debugging a connection pool ####

``djorm-ext-pool`` if django debug is activated, automaticaly sends messages when: creates new connection, get connection from pool and return a connection to pool.  To view messages in console, you must configure the logger "djorm.pool" in Django logging settings.

This is a simple example:

~~~ { python }
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'djorm.pool': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}
~~~

<br />

* Github: https://github.com/niwibe/djorm-ext-pool
* Last update: 2012/10/08

