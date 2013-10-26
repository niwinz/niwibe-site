# -*- coding: utf-8 -*-

import datetime
import pprint
import functools

from sqlalchemy import create_engine
from sqlalchemy.sql import text

engine = create_engine('postgresql+psycopg2://localhost/test', echo=False)


def bench(func=None, *, name=None):
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
