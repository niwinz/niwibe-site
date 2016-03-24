Title: Implementing OCC (Optimisic Concurrency Control) on the database
Tags: postgresql, concurrency
Author: Andrey Antukh

This is a simple tip for implement [OCC][1] directly on the database and so
avoiding additional overhead that this can imply doing that at the application
level.

The `OCC` mechanism mainly consists in:

- having an additional column called `version` by convention.
- check if the incoming modification has the same version value.
- increment that number on successfull modifications.

This can be done at the application level, but that will imply at least
an additional query for retrieve the row for match the version number.

To implement that on the database (in this case PostgreSQL), let start
defining a very simple trigger function that just checks the
version and raise exception if version mismatch:

```postgresql
CREATE OR REPLACE FUNCTION handle_occ()
  RETURNS TRIGGER AS $occ$
  BEGIN
    IF (NEW.version != OLD.version) THEN
      RAISE EXCEPTION 'Version mismatch: expected % given %',
            OLD.version, NEW.version
            USING ERRCODE='P0002';
    ELSE
      NEW.version := NEW.version + 1;
    END IF;
    RETURN NEW;
  END;
$occ$ LANGUAGE plpgsql;
```

Then, we should create a sample table with `version` field and attach
the appropriate trigger to it:

```postgresql
CREATE TABLE foobar (
  id bigserial,
  version bigint DEFAULT 0,
  name text
);

CREATE TRIGGER foobar_occ_tgr BEFORE UPDATE ON foobar
  FOR EACH ROW EXECUTE PROCEDURE handle_occ();
```

And we are done, let try that:

```psql
test=# INSERT INTO foobar (name) VALUES ('Yennefer');
INSERT 0 1

test=# SELECT * FROM foobar;
 id | version |   name
----+---------+----------
  1 |       0 | Yennefer
(1 row)

test=# UPDATE foobar SET version=3, name='Ciri' WHERE id = 1;
ERROR:  Version mismatch: expected 0 given 3
```

At the application level you can catch and handle this kind of errors
using the explicitly defined `ERRCODE` on the exception raised inside
the trigger function.

[1]: https://en.wikipedia.org/wiki/Optimistic_concurrency_control
