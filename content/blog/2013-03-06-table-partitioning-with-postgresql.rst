Table partitioning with PostgreSQL
----------------------------------

:tags: postgresql


PostgreSQL supports partitioning via table inheritance. So the partitioning is made in such a way that every child table inherits single parent table. Parent table is empty and it exists just to describe the whole data set.

The real benefit of table partitioning is a performance improvement with tables with amount of huge data. Decreases a index size, because you create a distinct index for each partition and making it more likely that the heavily-used parts of the indexes fit in memory. Can see more information on official documentation: http://www.postgresql.org/docs/9.2/static/ddl-partitioning.html

PostgreSQL table partitioning can be implemented in two ways: **range partitioning** or **list partitioning**. **Range partitioning** can be done by ranges like (1-1000, 1001-2000, ...) and **list partitioning** can be done with explicit list of keys. There are no real differences between the two ways, you have to choose one depending on the problem to be solved.


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
where we keep logs. Supose we have this table:

.. code-block:: postgresql

    CREATE SEQUENCE action_log_idseq;
    CREATE TABLE action_log (
        id bigint NOT NULL PRIMARY KEY DEFAULT nextval('action_log_idseq'),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        content text
    );
    ALTER SEQUENCE action_log_idseq OWNED BY action_log.id;


Next, create child tables. In our example we will be partitioned by range using the year of creation.

.. code-block:: postgresql

    CREATE SEQUENCE action_log_2012_idseq;
    CREATE TABLE action_log_2012 (
        id bigint NOT NULL PRIMARY KEY DEFAULT nextval('action_log_idseq'),
        CHECK(to_char(created_at, 'YYYY') = '2012')
    ) INHERITS (action_log);
    ALTER SEQUENCE action_log_2012_idseq OWNED BY action_log_2012.id;


We only insert, select, update and delete on MasterTable, all child tables are transparent to user.
