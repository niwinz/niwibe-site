Title: Get current timestamp in PostgreSQL
Tags: postgresql, time
Author: Andrey Antukh

I'm pretty sure that almost everyone that have used PostgreSQL knows the `now()`
function. Its purpose is mostly obvious: return the current timestamp or at least
its name indicates that.

```psql
test=# select now();
              now
-------------------------------
 2016-03-27 12:54:50.449097+00
(1 row)

test=# select now();
              now
-------------------------------
 2016-03-27 12:58:52.217013+00
(1 row)
```

But what is happens if we execute it inside of a transaction:

```psql
test=# BEGIN;
BEGIN

test=# select now();
              now
-------------------------------
 2016-03-27 12:59:41.852762+00
(1 row)

test=# select now();
              now
-------------------------------
 2016-03-27 12:59:41.852762+00
(1 row)

test=# COMMIT;
COMMIT
```

Surprised?? This is happens because `now()` function always returns the transaction
timestamp and the first example works because the statements are executed in an
implicit transaction if no explicit transaction is open.

If you need accurate timestamp, you should use `clock_timestamp()` function for
that purpose:

```psql
test=# BEGIN;
BEGIN

test=# select clock_timestamp();
       clock_timestamp
-----------------------------
 2016-03-27 13:10:15.6477+00
(1 row)

test=# select clock_timestamp();
        clock_timestamp
-------------------------------
 2016-03-27 13:10:16.407557+00
(1 row)

test=# COMMIT;
COMMIT
```

It always return the current wall-clock time based timestamp.

Incorrect use of `now()` function can cause some unexpected situations having not
monotonically increasing timestamps in log/audit tables (e.g. [here][1]).

[1]: http://blog.thefourthparty.com/stopping-time-in-postgresql/
