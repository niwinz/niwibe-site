---
layout: post.html
title: Order by subquery array with PostgreSQL
tags: [postgresql]
---

Sometimes we need to get a certain number of elements of the database by its primary key and another field. We have the values and the order in which we want to get the data.

To see examples, create a test table and insert sample values:

~~~ { sql }
test=# CREATE TABLE test_table (num int);
CREATE TABLE
test=# INSERT INTO test_table (num) VALUES (1), (2), (3), (4);
INSERT 0 4
test=# select num from test_table ;
 num 
-----
   1
   2
   3
   4
(4 rows)
~~~

We can see that the default order, is by insert.

Now imagine that we want to obtain a subset of the data in a specific order. We use the sentence "IN" to make the query.

~~~ { sql }
test=# SELECT num FROM test_table WHERE num in (4,2);
 num 
-----
   2
   4
(2 rows)
~~~

We notice that the order of the result does not correspond with what we really want. The first approach is to use conditional expressions with ORDER BY (CASE).

~~~ { sql }
test=# SELECT num FROM test_table WHERE num in (4,2) ORDER BY CASE num WHEN 4 THEN 1 WHEN 2 THEN 2 END;
 num 
-----
   4
   2
(2 rows)
~~~

Now we have the order and the expected result, but it is not usable, especially when the list ids can be variable. Building this sql for each case is really not usable.

The next approach, we will solve this problem. We define the following function:

~~~ { sql }
CREATE OR REPLACE FUNCTION idx(anyarray, anyelement)
  RETURNS int AS 
$$
  SELECT i FROM (
     SELECT generate_series(array_lower($1,1),array_upper($1,1))
  ) g(i)
  WHERE $1[i] = $2
  LIMIT 1;
$$ LANGUAGE sql IMMUTABLE;
~~~

Now we see an example of the above query but using this function:

~~~ { sql }
test=# SELECT num FROM test_table WHERE num in (4,2) ORDER BY idx('{4,2}'::int[], num);
 num 
-----
   4
   2
(2 rows)
~~~

This latter case is much more usable in my opinion.

#### Links ####

* http://www.postgresql.org/docs/9.2/static/functions-conditional.html
* http://stackoverflow.com/questions/2408965/postgres-subquery-ordering-by-subquery
