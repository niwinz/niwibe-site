Table partitioning with PostgreSQL
##################################

:tags: postgresql

PostgreSQL supports partitioning via table inheritance. So the partitioning is made in such a way that every child table inherits single parent table. Parent table is empty and it exists just to describe the whole data set.

The real benefit of table partitioning is a performance improvement with tables with amount of huge data. Decreases a index size, because you create a distinct index for each partition and making it more likely that the heavily-used parts of the indexes fit in memory.


PostgreSQL table partitioning can be implemented in two ways: **range partitioning** or **list partitioning**.

Range partitioning can be done by ranges like (1-1000, 1001-2000, ...) and list partitioning can be done with explicit list of keys. There are no real differences between the two ways, you have to choose one depending on the problem to be solved.

Basic steps for setup table partitioning
----------------------------------------

* Create a master table with all fields.
* Create a some childs tables with inheritance and without any additional field.
* Create indexes on each child.
* Create a trigger function for correct insert data on child tables.
* Enable constrain exclusion that improves performance on queries.


Simple example of data partitioning
-----------------------------------

Let's look at a basic example of how to set partitioning tables. To assume that we have a table
where we keep logs by country. Supose we have this table:

.. code-block:: postgresql

    CREATE TABLE action_log (
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        country_code char(2),
        content text
    );

    CREATE INDEX action_log_country_code ON action_log USING btree (country_code);


On next step, create child tables and trigger:

.. code-block:: postgresql

    --- Child tables
    CREATE TABLE action_log_fr ( CHECK ( country_code = 'fr') ) INHERITS (action_log);
    CREATE TABLE action_log_es ( CHECK ( country_code = 'es' ) ) INHERITS (action_log);

    CREATE INDEX action_log_fr_country_code ON action_log_fr USING btree (country_code);
    CREATE INDEX action_log_es_country_code ON action_log_es USING btree (country_code);

    --- Trigger function
    CREATE OR REPLACE FUNCTION on_actionlog_insert() RETURNS TRIGGER AS $$
    BEGIN
        IF ( NEW.country_code = 'es' ) THEN
            INSERT INTO action_log_es VALUES (NEW.*);
        ELSIF ( NEW.country_code = 'fr' ) THEN
            INSERT INTO action_log_fr VALUES (NEW.*);
        ELSE
            RAISE EXCEPTION 'Country unknown';
        END IF;

        RETURN NULL;
    END;
    $$ LANGUAGE plpgsql;

    --- Attach trigger function to table
    CREATE TRIGGER action_log_insert
        BEFORE INSERT ON action_log
        FOR EACH ROW EXECUTE PROCEDURE on_actionlog_insert();

At this point, you can insert some data into action_log table. You will see what your data is
automaticaly redirected to correponding child tabl. Is totally transparent for user.

.. code-block:: psql

    test=# INSERT INTO action_log (country_code, content) VALUES ('en', 'content-en');
    ERROR:  Country unknown
    test=# INSERT INTO action_log (country_code, content) VALUES ('es', 'content-es');
    INSERT 0 0
    test=# INSERT INTO action_log (country_code, content) VALUES ('fr', 'content-fr');
    INSERT 0 0


Now, if you make select on a master table (action_log), obtains all rows from
childs:

.. code-block:: psql

    test=# SELECT * FROM action_log_es;
              created_at           | country_code |  content
    -------------------------------+--------------+------------
     2013-03-07 22:54:45.859553+01 | es           | content-es
    (1 row)

    test=# SELECT * FROM action_log;
              created_at           | country_code |  content
    -------------------------------+--------------+------------
     2013-03-07 22:55:32.471027+01 | fr           | content-fr
     2013-03-07 22:54:45.859553+01 | es           | content-es
    (2 rows)


If you analyze a query plan of any select, you will see that postgresql scans all
child tables:

.. code-block:: psql

    test=# EXPLAIN ANALYZE SELECT * FROM action_log WHERE country_code = 'es';
                                                QUERY PLAN
    ----------------------------------------------------------------------------------------------------------
     Result  (cost=0.00..25.52 rows=11 width=52) (actual time=0.041..0.047 rows=1 loops=1)
       ->  Append  (cost=0.00..25.52 rows=11 width=52) (actual time=0.037..0.040 rows=1 loops=1)
             ->  Seq Scan on action_log  (cost=0.00..0.00 rows=1 width=52) (actual time=0.002..0.002 rows=0...
                   Filter: (country_code = 'es'::bpchar)
             ->  Bitmap Heap Scan on action_log_fr action_log  (cost=4.29..12.76 rows=5 width=52) (actual t...
                   Recheck Cond: (country_code = 'es'::bpchar)
                   ->  Bitmap Index Scan on action_log_fr_country_code  (cost=0.00..4.29 rows=5 width=0) (a...
                         Index Cond: (country_code = 'es'::bpchar)
             ->  Bitmap Heap Scan on action_log_es action_log  (cost=4.29..12.76 rows=5 width=52) (actual t...
                   Recheck Cond: (country_code = 'es'::bpchar)
                   ->  Bitmap Index Scan on action_log_es_country_code  (cost=0.00..4.29 rows=5 width=0) (a...
                         Index Cond: (country_code = 'es'::bpchar)
     Total runtime: 0.108 ms
    (13 rows)

This behavior is not optimal but postgresql have one option that help exclude child tables by contrain
defined with CHECK statement. You can activate it with:

.. code-block:: psql

    test=# SET constraint_exclusion = ON;
    SET


Now, this is a query-plan of previos query but with **constraint_exclusion** activated:

.. code-block:: psql

    test=# EXPLAIN ANALYZE SELECT * FROM action_log WHERE country_code = 'es';
                                                QUERY PLAN
    ----------------------------------------------------------------------------------------------------------
     Result  (cost=0.00..12.76 rows=6 width=52) (actual time=0.030..0.035 rows=1 loops=1)
       ->  Append  (cost=0.00..12.76 rows=6 width=52) (actual time=0.026..0.029 rows=1 loops=1)
             ->  Seq Scan on action_log  (cost=0.00..0.00 rows=1 width=52) (actual time=0.002..0.002 rows=0...
                   Filter: (country_code = 'es'::bpchar)
             ->  Bitmap Heap Scan on action_log_es action_log  (cost=4.29..12.76 rows=5 width=52) (actual t...
                   Recheck Cond: (country_code = 'es'::bpchar)
                   ->  Bitmap Index Scan on action_log_es_country_code  (cost=0.00..4.29 rows=5 width=0) (a...
                         Index Cond: (country_code = 'es'::bpchar)
     Total runtime: 0.081 ms
    (9 rows)


In conclusion, setup table partitioning with postgresql is very simple and improved considerably performance with tables with huge amount of data.

Can see more information on official documentation: http://www.postgresql.org/docs/9.2/static/ddl-partitioning.html

Related links
-------------

* http://www.if-not-true-then-false.com/2009/howto-create-postgresql-table-partitioning-part-1/
* http://www.if-not-true-then-false.com/2009/performance-testing-between-partitioned-and-non-partitioned-postgresql-tables-part-3/
* http://www.mkyong.com/database/partition-table-in-postgresql-create-partition-part-1/
* http://www.mkyong.com/database/partition-table-in-postgresql-simulate-millions-data-part-2/
* http://www.mkyong.com/database/performance-testing-on-partition-table-in-postgresql-part-3/
* http://www.linuxforu.com/2012/01/partitioning-in-postgresql/

