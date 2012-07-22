---
layout: post.html
title: Project - django-orm-extensions
tags: [python, django, postgresql, orm]
---

This small project consists in maintaining some pluggins to the ORM of django, with several enhancements that will be explained below.

My main motivation in creating this project is to see to unify several “plugins” in one package, so it can be used independently if you want one or more of them.

I certainly do not want to take all the credit, because not all the work I have done, however if you’ll take care of having a single integrated package with a stable api and covers the most popular databases: postgresql, mysql and sqlite3.

This is an evolution of the project django-postgresql. So do not limit myself to a single database and applied some improvements to all backends.

**Documentation: (latest)** <http://readthedocs.org/docs/django-orm/en/latest/>

### Instalation ###

    pip install django-orm-extensions

*NOTE*: I recommend using the git version because the version of PyPI not fully updated.

## Features ##

#### All backends ####

 * Low level orm cache (postgresql, mysql, sqlite)
 * Function and Expression definition as python class´es
 * New method for make complex querys using self defined functions and expressions.

#### PostgreSQL specific ####

 * PostgreSQL HStore.
 * PostgreSQL Full Text Search.
 * PostgreSQL Server side cursors.
 * PostgreSQL Complex types fields:
    * Array
    * Interval
    * Bytea
    * Geometric

#### MySQL specific ####

**Under development**


## Requirements ##

#### PostgreSQL specific ####

 * PostgreSQL >= 9.0 (if postgresql is used)
 * Psycopg2 >= 2.4 (if postgresql is used)

#### MySQL specific ####

 * MySQL >= 5.1
 * MySQL-python (MySQLdb) >= 1.2.3

#### Generic ####

 * Django >= 1.3
 * Django-Redis

## Under development ##

 * Composite types of PostgreSQL (under develpment on devel branch)

## Future plans (TODO) ##

 * Object locking (postgresql, mysql, sqlite)
 * Add custom triggers in the definition of the model. (In consideration.)
 * PL/Python function and triggers definition with python clasess and methods. (In consideration.)(postgresql)
 * N-Dimensional Cube - <http://www.postgresql.org/docs/9.1/static/cube.html>
 * Database independent index creation layer.
 * Database independent within that possible View implementation.
 * Database independent full text search syntax (that compiles to native syntax depending on the backend).


## Changelog ##

 - **master** - <https://github.com/niwibe/django-orm-extensions>


[1]:https://github.com/oliy/django-hstore
