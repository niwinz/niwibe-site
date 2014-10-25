Title: Backup strategies and High Availability with PostgreSQL
Tags: postgresql, backup, high-availability

The first step for high availability is have good backup strategy.

There is no silver bullet. Each environment requires ad-hoc strategies depending of various factors
like: the size of the database, data criticity, and much others. In this article I will try explain
the basic recipe of good practices, and you should adapt it to your needs.

## Backup strategy ##

There are different backup strategies:

- SQL Level backup (with **pg_dump** or **pg_dumpall**)
- File System backup (using standard unix tools)
- Continuous Archiving and Point-in-Time Recovery (PITR)

### SQL Level Backup ###

This is the most basic way to make a consistent backup of your database or the entire cluser.

```bash
pg_dump -O -Fc -f database.dump yourdatabasename
```

This command uses the postgresql custom format (officially recommended by postgresql) that
automatically commpress the result.

You can restore the backup using the **pg_restore** command.

```bash
pg_restore -d yourdatabasename ./database.dump
```

This method is really simple and useful where the database size is small and allows constantly
dumps. But when the database size grows, this method turns to be not feasible, and you should consider
using an other method.

Additionally **pg_dump** is a greet tool for detect corruption.

### Continuos Wal Archiving ###

In summary, this method allows store incremental backups.

But in detail this has more advantatges:

- It allows point in time recovery (last 20min as example).
- It allows setup standby servers for quick failover.
- It allows make complete backups less frecuently.
- It allows use easy filesystem snapshots (zfs).

