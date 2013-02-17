Show database, table and indexes size on PostgreSQL
###################################################

:tags: postgresql

Many times I have needed show how spaces is used on my databases, tables or indexes. Here I will try to
explain in a concise and simple way to obtain this useful information.

Show database size
------------------

The simples way to show a database size, is executing this query:

.. code-block:: sql

    SELECT pg_size_pretty(pg_database_size('dbname'));


``pg_database_size`` function returns a size in bytes and ``pg_size_pretty`` put this
value on more readable by humans.

This is a possible result of this query:


.. code-block:: psql

    dbname=> SELECT pg_size_pretty(pg_database_size('dbname'));
     pg_size_pretty
    ----------------
     76 MB
    (1 row)


Show relation size
------------------

There are two ways to view a relation size. Relation as is, is a table or index on postgresql.

Show table size, without indexes:

.. code-block:: psql

    dbname=> select pg_size_pretty(pg_relation_size('cities_region'));
     pg_size_pretty
    ----------------
     4224 kB
    (1 row)


Show table size with indexes:

.. code-block:: psql

    dbname=> select pg_size_pretty(pg_total_relation_size('cities_region'));
     pg_size_pretty
    ----------------
     18 MB
    (1 row)


With same way, you can show index size:

.. code-block:: psql

    dbname=> select pg_size_pretty(pg_relation_size('cities_region_name'));
     pg_size_pretty
    ----------------
     1688 kB
    (1 row)


Show list of biggest relations on your database
-----------------------------------------------

Query thats shows last ten with their corresponding size.

.. code-block:: sql

    SELECT relname AS "relation", pg_size_pretty(pg_relation_size(C.oid)) AS "size"
      FROM pg_class C LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace)
      WHERE nspname NOT IN ('pg_catalog', 'information_schema')
      ORDER BY pg_relation_size(C.oid) DESC
      LIMIT 10;

This query output includes indexes and tables.

Exameple output:

.. code-block:: psql

    dbname=> SELECT relname AS "relation", pg_size_pretty(pg_relation_size(C.oid)) AS "size"
    dbname->   FROM pg_class C LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace)
    dbname->   WHERE nspname NOT IN ('pg_catalog', 'information_schema')
    dbname->   ORDER BY pg_relation_size(C.oid) DESC
    dbname->   LIMIT 10;
                       relation                   |  size
    ----------------------------------------------+---------
     cities_region                                | 4224 kB
     cities_city                                  | 3848 kB
     cities_city_region_id_name_key               | 1888 kB
     cities_region_name_like                      | 1768 kB
     cities_region_slug_like                      | 1760 kB
     cities_region_slug                           | 1744 kB
     django_session                               | 1736 kB
     cities_region_name                           | 1688 kB
     cities_city_country_id_401060b88e5285df_uniq | 1432 kB
     cities_region_geoname_id_key                 | 1384 kB
    (10 rows)


Also, this is a query thats shows last five tables with their corresponding size including indexes:

.. code-block:: sql

    SELECT relname AS "relation",
        pg_size_pretty(pg_total_relation_size(C.oid)) AS "total_size"
      FROM pg_class C
      LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace)
      WHERE nspname NOT IN ('pg_catalog', 'information_schema')
        AND C.relkind <> 'i'
        AND nspname !~ '^pg_toast'
      ORDER BY pg_total_relation_size(C.oid) DESC
      LIMIT 5;

This is a posible output:

.. code-block:: psql

    dbname=> SELECT relname AS "relation",
    dbname->     pg_size_pretty(pg_total_relation_size(C.oid)) AS "total_size"
    dbname->   FROM pg_class C
    dbname->   LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace)
    dbname->   WHERE nspname NOT IN ('pg_catalog', 'information_schema')
    dbname->     AND C.relkind <> 'i'
    dbname->     AND nspname !~ '^pg_toast'
    dbname->   ORDER BY pg_total_relation_size(C.oid) DESC
    dbname->   LIMIT 5;
        relation     | total_size
    -----------------+------------
     cities_region   | 18 MB
     cities_city     | 17 MB
     auth_user       | 3048 kB
     django_session  | 3024 kB
     profile_profile | 3016 kB
    (5 rows)


Related links
^^^^^^^^^^^^^

- http://wiki.postgresql.org/wiki/Disk_Usage
