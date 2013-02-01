Title: Sql expressions and functions with Django.
Tags: python, django, orm

Django by default, provides a wide range of field types and generic lookups for queries. This in many cases is more than enough. But there are cases where you need to use types defined for yourself and search operators that are not defined in django lookups and another important case is to make searches requiring the execution of some function in WHERE clause. 

``djorm-ext-expressions`` tries to solve these problems, adding the ability to build complex expressions and use database functions through a simple API.


The current api exposes the following classes:

* ``djorm_expressions.base.RawExpression``
* ``djorm_expressions.base.SqlExpression``
* ``djorm_expressions.base.SqlFunction``
* ``djorm_expressions.base.AND``
* ``djorm_expressions.base.OR``
* ``djorm_expressions.models.ExpressionQuerySetMixin``
* ``djorm_expressions.models.ExpressionManagerMixin``
* ``djorm_expressions.models.ExpressionQuerySet``
* ``djorm_expressions.models.ExpressionManager``


## Custom aggregate functions. ##

As I said before, native django orm annotations only supports predefined types that return integers or float. To solve this problem, ``djorm-ext-expressions`` introduces new method ``annotate_functions`` available on the custom manager and queryset, and ``SqlFunction`` class for define custom functions.

    :::python
    from django.db import models
    from djorm_expressions.models import ExpressionManager
    from djorm_expressions.base import SqlFunction

    # Define a python class that represents a database function.

    class BitLength(SqlFunction):
        sql_function = "bit_length"


    class Person(models.Model):
        name = models.CharField(max_length=200)
        objects = ExpressionManager()

And here, a simple usage example:

    :::python
    queryset = Person.objects.annotate_functions(
        bitlength = BitLength("name")
    )

Each object of a queryset, now contains a ``bitlength`` attribute with corresponding value, without any limitation of aggregate subsystem of django.

## Complex expressions using predefined functions ##

With the same model in the previous example, we imagine that we want to make a search using the ``bit_length`` function. With django standard API, we are required to write SQL for this case.

With ``djorm-ext-expressions`` we do not have that problem, and for that you have entered the method ``where()`` and class ``SqlExpression``.

Here, simle query, using ``BitLength`` function class:

    :::python
    queryset = Person.objects.where(
        SqlExpression(BitLength("name"), ">", 20)
    )

Obviously, you can no use the ``BitLength`` function, and perform a simple query:

    :::python
    queryset = Person.objects.where(
        SqlExpression("name", "=", u"pepe")
    )

Additionally, it may increase the complexity of the query, using ``AND`` and ``OR`` expresions:

    :::python
    expression = OR(
        SqlExpression(BitLength("name"), ">", 20),
        SqlExpression(BitLength("name"), "<", 100),
    )

    queryset = Person.objects.where(expression)

**NOTE**: you can use the django double underscore notation on the field name for automaticaly setup joins.

## Using expressions with custom operators not defined on django lookup subsystem ##

PostgreSQL has many types, in addition to the SQL standard, such as arrays. For arrays, there are several operators to perform complex searches. A clear example: search if an array is contained by the other.

``SqlExpression`` helps us for this kind of search:

    :::python
    from django.db import models
    from djorm_expressions.models import ExpressionManager
    from djorm_pgarray.fields import ArrayField

    class Register(models.Model):
        name = models.CharField(max_length=200)
        points = ArrayField(dbtype="int")
        objects = ExpressionManager()

    # Simple query using contains operator
    qs = Register.objects.where(
        SqlExpression("points", "@>", [2,3])
    )

**NOTE**: ``ArrayField`` is part of ``djorm-ext-pgarray`` module available in pypi.

And, finally can redefine the "SqlExpression" class, and make it more "object oriented":

    :::python
    class ArrayExpression(object):
        def __init__(self, field):
            self.field = field

        def contains(self, value):
            return SqlExpression(self.field, "@>", value)

        def overlap(self, value):
            return SqlExpression(self.field, "&&", value)

    # search all register items that points field contains [2,3]
    queryset = Register.objects.where(
        ArrayExpression("points").contains([2,3])
    )


How to install
==============

You can clone the repo from github and install with simple ``python setup.py install`` command. Or use a `pip`, for install it from Python Package Index.

``pip install djorm-ext-expressions``


* Github: <https://github.com/niwibe/djorm-ext-expressions>
* Last update: 2012/10/07
