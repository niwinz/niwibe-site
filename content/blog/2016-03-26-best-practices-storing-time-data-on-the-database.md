Title: Best practices storing time data on the database
Tags: postgresql, time
Author: Andrey Antukh
Status: draft

There is my personal list of best practices handling with time
related data and its persistence. I assume they are for
PostgreSQL in first time but that recommendations are
almost the same for other databases:

- Set your database timezone to `UTC` or at least set the connection
  timezone to `UTC` and persists datetimes always in `UTC`.
- Perform any time related logic with datetimes in `UTC`
- Treat all non-zero UTC datetimes as an input error.
- Only translate datetimes to specific timezone when you go to
  show them to the user.
- Persist the user timezone with apropriate timezone name
  (e.g. `America/Los_Angeles`, not `+0200`).

In case of PostgreSQL, the time handling is fantastic and using
the `timestamptz` should be your almost always the default option.

PostgreSQL by default stores all datetimes in UTC and only transforms
them to different timezone when user request that:

```psql
test=# create table foobar (
test(#   id bigint,
test(#   created_at timestamptz default current_timestamp
test(# );
CREATE TABLE

test=# insert into foobar (id) values (1);
INSERT 0 1
test=# select * from foobar;
 id |          created_at
----+-------------------------------
  1 | 2016-03-23 13:49:26.865655+00

test=# set timezone = "Europe/Moscow";
SET
test=# select * from foobar;
 id |          created_at
----+-------------------------------
  1 | 2016-03-23 16:49:26.865655+03

```

So if you are storing datetimes without timezone, PostgreSQL will
assume the current timezone of the database and this may not match
with the user's timezone; that in some ocasions can cause bugs showing
unexpected datetimes.

Also, we can't rely on the postgresql connection timezone because
postgres knows nothing about the application's user timezone, so
the most recommended approach here is setup `UTC` as default
timezone in the database and leave to the application the
responsability to convert datetimes to approriate timezone for
presentation purposes only.

To ensure that the application logic always persists using UTC, we
can force for certain fields that the inserted values should always
come in UTC timezone. This can be done using the `CHECK` clause:

```sql
CREATE TABLE foobar (
  id bigint,
  some_date timestamptz,
  -- [...]

  CHECK(EXTRACT(TIMEZONE FROM some_date) = '0')
);
```

This is not a perfect solution but can you save from some bugs
and in general is a very good practice.

Another most common mistake is rely on the ORM defaults.
A great example is [Hibernate][1], that setup's the datetime
columns without timezone in the default dialect.

[1]: http://hibernate.org/
