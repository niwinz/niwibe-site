Table inheritance with PostgreSQL
#################################

:tags: postgresql

Table inheritance is one of the features in PostgreSQL has impressed me a lot, I have
discovered its potential recently, research on partitioning tables (I explain it on the next article).
The idea of this article is to see how it works, and how we can take advantage of this feature.

Sure we've had many times the problem having different heterogeneous objects with a common base
(of database fields). Instead of a simple solution,  mantain a separate table for a heterogeneous fields
and make a join query when you want obtain a list of some data on one child table, you can use this
feature. With PostgreSQL, table inheritance can be defined in very easy way, see this simple example that defines
a master table post and two childs: one child without additional fields and other with tag fields:

.. code-block:: postgresql

    CREATE TABLE post (id integer, title varchar(100), content text);
    CREATE TABLE post_without_tags () INHERITS (post);
    CREATE TABLE post_with_tags (tags text[]) INHERITS (post);

    --- Insert sample data

    INSERT INTO post_without_tags (id, title, content)
        VALUES (1, 'title-1', 'content-1');
    INSERT INTO post_without_tags (id, title, content)
        VALUES (2, 'title-2', 'content-2');

    INSERT INTO post_with_tags (id, title, content, tags)
        VALUES (3, 'title-3', 'content-3', '{"foo","bar"}'::text[]);
    INSERT INTO post_with_tags (id, title, content, tags)
        VALUES (4, 'title-4', 'content-4', '{"foo","bar"}'::text[]);


Now, you can make query to the last created tables:

.. code-block:: psql

    test=# select * from post_with_tags;
     id |  title  |  content  |   tags
    ----+---------+-----------+-----------
      3 | title-3 | content-3 | {foo,bar}
      4 | title-4 | content-4 | {foo,bar}
    (2 rows)

    test=# select * from post_without_tags;
     id |  title  |  content
    ----+---------+-----------
      1 | title-1 | content-1
      2 | title-2 | content-2
    (2 rows)

But if you make a query on a master table (post table), we will obtain all posts, from
each child table. See example:

.. code-block:: psql

    test=# select * from post;
     id |  title  |  content
    ----+---------+-----------
      1 | title-1 | content-1
      2 | title-2 | content-2
      3 | title-3 | content-3
      4 | title-4 | content-4
    (4 rows)

And this is a result of **explain**:

.. code-block:: psql

    test=# explain analyze select * from post;
                                                               QUERY PLAN
    ---------------------------------------------------------------------------------------------------------------------------------
     Result  (cost=0.00..25.30 rows=531 width=254) (actual time=0.012..0.034 rows=4 loops=1)
       ->  Append  (cost=0.00..25.30 rows=531 width=254) (actual time=0.009..0.023 rows=4 loops=1)
             ->  Seq Scan on post  (cost=0.00..0.00 rows=1 width=254) (actual time=0.002..0.002 rows=0 loops=1)
             ->  Seq Scan on post_without_tags post  (cost=0.00..12.80 rows=280 width=254) (actual time=0.004..0.007 rows=2 loops=1)
             ->  Seq Scan on post_with_tags post  (cost=0.00..12.50 rows=250 width=254) (actual time=0.003..0.006 rows=2 loops=1)
     Total runtime: 0.066 ms
    (6 rows)

As we can see, postgresql automatically search on both childs and return result with a common fields defined
on a master table.

Also, you can make other operations over post table, and all changes are propagated automatically to child tables. See a sample
example making a update:

.. code-block:: psql

    test=# update post set title  = title || '-foo';
    UPDATE 4

    test=# select * from post;
     id |    title    |  content
    ----+-------------+-----------
      1 | title-1-foo | content-1
      2 | title-2-foo | content-2
      3 | title-3-foo | content-3
      4 | title-4-foo | content-4
    (4 rows)

    test=# select * from post_without_tags ;
     id |    title    |  content
    ----+-------------+-----------
      1 | title-1-foo | content-1
      2 | title-2-foo | content-2
    (2 rows)


As I said at the beginning of the article, the real potential of this feature is going to be with a table partitioning.

Related links
-------------

* http://www.postgresql.org/docs/9.2/static/ddl-inherit.html
