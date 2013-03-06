Index usage statistics in PostgreSQL
####################################

:tags: postgresql

This is a simple tip for obtain statistic information about indexes usage on a
current database. All information is obtained from some views exposed by PostgreSQL,
and populated by the Statistics Collector.

Tips of this post only exposes some facility for obtain these information (filtered
by current database and exclude system indexes).

Helper sql functions
--------------------

Sql function that returns a table with I/O infomation (obtained from pg_statio_user_indexes view)
and filtered by current database and "public" schema:

.. code-block:: postgresql

    CREATE OR REPLACE FUNCTION indexes_io_for_current_database()
    RETURNS TABLE(indexname name, idx_blks_read bigint, idx_blks_hit bigint) AS $$
        SELECT i.indexrelname, i.idx_blks_read, i.idx_blks_hit
        FROM pg_statio_user_indexes AS i
        WHERE i.relname IN (SELECT table_name FROM information_schema.tables WHERE table_schema = 'public');
    $$ LANGUAGE SQL;


Sql function that returns a table with index usage infomation (obtained from pg_stat_user_indexes view)
and filtered by current database and "public" schema:

.. code-block:: postgresql

    CREATE OR REPLACE FUNCTION indexes_stat_for_current_database()
    RETURNS TABLE(indexname name, idx_scan bigint, idx_tup_read bigint, idx_tup_fetch bigint) AS $$
        SELECT i.indexrelname, i.idx_scan, i.idx_tup_read, i.idx_tup_fetch
        FROM pg_stat_user_indexes AS i
        WHERE i.relname IN (SELECT table_name FROM information_schema.tables WHERE table_schema = 'public');
    $$ LANGUAGE SQL;


Examples
--------

The simple way to obtain a last 5 most used indexes on your database:

.. code-block:: psql

    foodb=> select * from indexes_stat_for_current_database() order by idx_scan DESC LIMIT 5;
               indexname           | idx_scan | idx_tup_read | idx_tup_fetch
    -------------------------------+----------+--------------+---------------
     auth_user_pkey                | 20074525 |    141906772 |     141898258
     profile_user_id_key           |  8147399 |      7923886 |       7918973
     actionlog_created_date        |  6452507 |      6452508 |       6452505
     actionlog_to_user_id          |  4438980 |    282814752 |            20
     actionlog_from_user_id        |  4018583 |     45458783 |      11955250
    (5 rows)

Also, simple way for obtain the 5 indexes with most hits from buffers (cache?)

.. code-block:: psql

    foodb=> select * from indexes_io_for_current_database() order by idx_blks_hit desc limit 5;
               indexname           | idx_blks_read | idx_blks_hit
    -------------------------------+---------------+--------------
     auth_user_pkey                |           441 |     41678422
     profile_user_id_key           |          1071 |     17219297
     actionlog_created_date        |           713 |     12950554
     actionlog_to_user_id          |          6993 |      9899807
     actionlog_from_user_id        |          2117 |      8234565
    (5 rows)


Links
-----

For more information you can see these links to the official postgresql documentation:

* http://www.postgresql.org/docs/9.2/static/monitoring-stats.html

