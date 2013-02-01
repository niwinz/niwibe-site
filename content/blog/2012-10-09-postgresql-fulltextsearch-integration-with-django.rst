PostgreSQL full text search with Django
#######################################

:tags: python, django, postgresql, orm


Full Text Searching (or just text search) provides the capability to identify natural-language documents that satisfy a query, and optionally to sort them by relevance to the query. The most common type of search is to find all documents containing given query terms and return them in order of their similarity to the query. Notions of query and similarity are very flexible and depend on the specific application. The simplest search considers query as a set of words and similarity as the frequency of query words in the document (from postgresql documentation).

`djorm-ext-pgfulltext` attempts to provide a simple way to perform text searches in postgresql with Django.

Exposed classes:
----------------

* ``djorm_pgfulltext.fields.VectorField``
* ``djorm_pgfulltext.models.SearchManagerMixIn``
* ``djorm_pgfulltext.models.SearchManager``

The ``VectorField`` represents a ``tsvector`` PostgreSQL type used for storing preprocessed documents. ``SearchManagerMixIn`` is, as is, manager mixin with all fts features, so you can build a manager who inherits from several mixins. And ``SearchManager`` is a complete manager that conains all functionality from a ``SearchManagerMixIn``.


How to use it
-------------

There are several ways of using them, explain two ways. In the first case, we will define what fields are indexed and we want to keep a field tsvector preprocessed and ready for searching. And segudo, much more flexible, it makes searches on any text field without maintaining tsvector field.

For performance, you must manually add GIST and GIN indexes for queries to be performed for both the field tsvector as for dynamic queries.

A first way
^^^^^^^^^^^

Define a example models:

.. code-block:: python

    from djorm_pgfulltext.models import SearchManager
    from djorm_pgfulltext.fields import VectorField
    from django.db import models

    class Page(models.Model):
        name = models.CharField(max_length=200)
        description = models.TextField()

        search_index = VectorField()

        objects = SearchManager(
            fields = ('name', 'description'),
            config = 'pg_catalog.english', # this is default
            search_field = 'search_index', # this is default
            auto_update_search_field = True
        )

* With `fields` parameter indicates what we want preprocess a ``search_index`` field with content from a ``name`` and ``description`` field.
* The ``config`` parameter is used for indicate which configuration is used by default on queries.
* With ``search_index`` indicates the name of field used for store a preprocesed data (a ``tsvector`` type field)
* With ``auto_update_search_field`` parameter we indicates to a manager to update automaticaly a ``search_index`` field on we calls ``save()`` method of model instance.

The ``SearchManager`` exposes a ``search(query, raw=False, using=None, fields=None, config=None)`` field. 

By default the query is parsed by ``plainto_tsquery`` postgresql function, but if you want to pass the query in raw, simply pass the parameter `raw` as True. As I said before, with the ``config`` parameter can change the query settings at the time of execution of the same. ``fields`` will explain later.

This is a simple example usage:


.. code-block:: python

    >>> Page.objects.search("documentation & about")
    [<Page: Page: Home page>]
    >>> Page.objects.search("about | documentation | django | home", raw=True)
    [<Page: Page: Home page>, <Page: Page: About>, <Page: Page: Navigation>]


Second way
^^^^^^^^^^

Here we will not use the VectorField if not that, we will specify which fields to use at the time of the search.

We define a model for the example:

.. code-block:: python

    class Page(models.Model):
        name = models.CharField(max_length=200)
        description = models.TextField()
        objects = SearchManager(fields=None, search_field=None)

And now we see an example of use, similar to above, but with slight differences:

.. code-block:: python

    >>> Page.objects.search("documentation & about", fields=('name', 'description'))
    [<Page: Page: Home page>]
    >>> Page.objects.search("about | documentation | django | home", raw=True, fields=('name', 'description'))
    [<Page: Page: Home page>, <Page: Page: About>, <Page: Page: Navigation>]

Obviously, we can add more rules to the query with django standard methods:

.. code-block:: python

    >>> query = "about | documentation | django | home"
    >>> Page.objects.search(query, raw=True, fields=('name', 'description')).filter(id__in=[1,2,3])
    [<Page: Page: Home page>, <Page: Page: About>]

How to install
--------------

Run ``python setup.py install`` to install, or place ``djorm_pgfulltext`` on your Python path.

You can also install it with: ``pip install djorm-ext-pgfulltext``


Conclusion
----------

This is the solution we have implemented several projects to solve this problem. If you think you can improve, I will be happy to discuss the issue and implement improvements.

* How to use a full text searches with postgresql (spanish) - http://kaleidos.net/blog/como-usar-busqueda-de-texto-en-postgresql/
* Github: https://github.com/niwibe/djorm-ext-pgfulltext
* Last update: 2012/10/09
