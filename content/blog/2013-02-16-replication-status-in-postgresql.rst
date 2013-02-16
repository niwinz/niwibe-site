Show replication status in PostgreSQL
#####################################

:tags: postgresql

This is a small tip to view the replication status of slave postgresql servers. The simplest way
to see the replication state on a master server is executing this query:

.. code-block:: sql

    select client_addr, state, sent_location, write_location,
            flush_location, replay_location from pg_stat_replication;

This query can output can be like this:

.. code-block:: psql

    postgres=# select client_addr, state, sent_location
    postgres-# write_location, flush_location, replay_location, sync_priority from pg_stat_replication;
     client_addr |   state   | write_location | flush_location | replay_location | sync_priority
    -------------+-----------+----------------+----------------+-----------------+---------------
     10.0.2.184  | streaming | AB/416D178     | AB/416D178     | AB/416D178      |             0
    (1 row)


If the slave is up in hot standby mode, you can tell the time in seconds the delay of transactions
applied on the slave with this query:

.. code-block:: sql

    select now() - pg_last_xact_replay_timestamp() AS replication_delay;

This is a possible output:

.. code-block:: psql

    postgres=# select now() - pg_last_xact_replay_timestamp() AS replication_delay;
     replication_delay
    -------------------
     00:00:08.057668
    (1 row)

In a very busy database, with many writes per second, this number will remain fairly accurate.
However, in a system where there are few writes, the "replication_delay" will continually grow
because the last replayed transaction timestamp isn't increasing (this is generally the same
limitation as MySQL's SHOW SLAVE STATUS output).
