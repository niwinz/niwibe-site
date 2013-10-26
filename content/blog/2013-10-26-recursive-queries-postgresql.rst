Recursive queries with PostgreSQL
#################################

:tags: postgresql

Sometimes we need store some graph/tree structures in your relational database (eg, postgresql)
and query childs of some top level node of your stored tree.

This problem, has various soultions.

The most simple way to get all child nodes of one top level node is execute query for each
tree depth. But for large trees with 5+ levels of nesting, this is pretty slow.

PostgreSQL offers recursive queries that helps a lot obtaining all child nodes.


Sample data
-----------

Here, we will try both methods for obtain a child nodes. For this experimet we will used these sql data:

.. code-block:: sql

    DROP TABLE IF EXISTS node;

    CREATE TABLE node (
        id integer,
        parent_id integer,
        name varchar(255),
        PRIMARY KEY(id)
    );

    INSERT INTO node VALUES
        (1, null, 'node 1'),
        (2, null, 'node 2'),
        (3,    1, 'node 3'),
        (4,    3, 'node 4'),
        (5,    2, 'node 5'),
        (6,    4, 'node 6'),
        (7,    6, 'node 7'),
        (8,    7, 'node 8'),
        (9,    1, 'node 9');


Experiment code
---------------

Watching this snippet, we can obseve two main functions, firts implements a simple way for obtain all chinlds
and second use postgresql recursive query for do same thing.

.. code-block:: python

    # -*- coding: utf-8 -*-

    import datetime
    import pprint
    import functools

    from sqlalchemy import create_engine
    from sqlalchemy.sql import text

    engine = create_engine('postgresql+psycopg2://localhost/test', echo=False)

    def bench(func=None, *, name=None):
        """
        Decorator used for benchmark execution of arbitrary function.
        """
        if func is None:
            return functools.partial(bench, name=name)

        def _wrapper(*args, **kwargs):
            t = datetime.datetime.now()
            result = func(*args, **kwargs)

            delta = (datetime.datetime.now() - t).total_seconds() * 1000.0
            print("[{}] Elapsed time: {} msecs.".format(name, delta))
            return result
        return _wrapper

    @bench(name="simple")
    def dump_simple():
        sm_s = text("select id, parent_id, name from node where parent_id = :parent_id order by name;")
        sm_n = text("select id, parent_id, name from node where id = :id;")

        def get_parents(conn, parent_id):
            result = conn.execute(sm_s, parent_id=parent_id)
            final_results = []

            for item in result:
                final_results.append(item)
                final_results.extend(get_parents(conn, item[0]))

            return final_results

        def dumps(conn, id):
            result = conn.execute(sm_n, id=id)
            first = result.fetchone()
            result.close()
            return [first] + get_parents(conn, id)

        with engine.begin() as conn:
            return dumps(conn, 1)

    @bench(name="recursive")
    def dump_recursive():
        sm_s = text("""
            WITH RECURSIVE nodes_cte AS (
                SELECT n.id, n.parent_id, n.name, n.id::TEXT AS path
                    FROM node AS n
                    WHERE n.parent_id = :id
                UNION ALL
                SELECT c.id, c.parent_id, c.name, (p.path || '->' || c.id::TEXT) AS path
                    FROM nodes_cte AS p, node AS c
                    WHERE c.parent_id = p.id
            )
            (
                SELECT id, parent_id, name, '' as path FROM node WHERE id = :id
                UNION ALL
                SELECT * FROM nodes_cte ORDER BY path ASC
            );
        """)

        with engine.begin() as conn:
            result = conn.execute(sm_s, id=1)
            try:
                return result.fetchall()
            finally:
                result.close()

    if __name__ == "__main__":
        pprint.pprint(dump_simple())
        pprint.pprint(dump_recursive())


Benchmarking
------------

This is a result of executing a code snippet:


.. code-block:: text

    [simple] Elapsed time: 25.171 msecs.
    [(1, None, 'node 1'),
     (3, 1, 'node 3'),
     (4, 3, 'node 4'),
     (6, 4, 'node 6'),
     (7, 6, 'node 7'),
     (8, 7, 'node 8'),
     (9, 1, 'node 9')]
    [recursive] Elapsed time: 2.727 msecs.
    [(1, None, 'node 1', ''),
     (3, 1, 'node 3', '3'),
     (4, 3, 'node 4', '3->4'),
     (6, 4, 'node 6', '3->4->6'),
     (7, 6, 'node 7', '3->4->6->7'),
     (8, 7, 'node 8', '3->4->6->7->8'),
     (9, 1, 'node 9', '9')]


Watching a postgresql log of execute `dump_simple` function:

.. code-block:: text

    LOG:  duration: 0.039 ms  statement: BEGIN
    LOG:  duration: 0.558 ms  statement: select id, parent_id, name from node where id = 1;
    LOG:  duration: 0.861 ms  statement: select id, parent_id, name from node where parent_id = 1 order by name;
    LOG:  duration: 0.238 ms  statement: select id, parent_id, name from node where parent_id = 3 order by name;
    LOG:  duration: 0.234 ms  statement: select id, parent_id, name from node where parent_id = 4 order by name;
    LOG:  duration: 0.235 ms  statement: select id, parent_id, name from node where parent_id = 6 order by name;
    LOG:  duration: 0.234 ms  statement: select id, parent_id, name from node where parent_id = 7 order by name;
    LOG:  duration: 0.229 ms  statement: select id, parent_id, name from node where parent_id = 8 order by name;
    LOG:  duration: 0.227 ms  statement: select id, parent_id, name from node where parent_id = 9 order by name;
    LOG:  duration: 0.027 ms  statement: COMMIT

And this is a postgresql log of executing a `dump_recursive` function:

.. code-block:: text

    LOG:  duration: 0.019 ms  statement: BEGIN
    LOG:  duration: 1.334 ms  statement:
                    WITH RECURSIVE nodes_cte AS (
                        SELECT n.id, n.parent_id, n.name, n.id::TEXT AS path
                            FROM node AS n
                            WHERE n.parent_id = 1
                        UNION ALL
                        SELECT c.id, c.parent_id, c.name, (p.path || '->' || c.id::TEXT) AS path
                            FROM nodes_cte AS p, node AS c
                            WHERE c.parent_id = p.id
                    )
                    (
                        SELECT id, parent_id, name, '' as path FROM node WHERE id = 1
                        UNION ALL
                        SELECT * FROM nodes_cte ORDER BY path ASC
                    );
    LOG:  duration: 0.031 ms  statement: COMMIT


We can observe, that using recursive query we can obtain a same results in more less time that using
a simple way (execute query for each depth) of obtain child nodes.
