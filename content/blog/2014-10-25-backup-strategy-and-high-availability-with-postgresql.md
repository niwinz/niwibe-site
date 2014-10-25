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

Backups using "Continuous wal archiving" needs two things to be done:

- Initial standalone backup (using **pg_basebackup**)
- All WAL files created after backup.

As first step for making it working, is change the postgresql configuration.

Set this options in your **postgresql.conf**:

```text
wal_level = archive
max_wal_senders = 24
wal_keep_segments = 16

archive_mode = on
archive_command = 'test ! -f /mnt/archivedir/%f && cp %p /mnt/server/%f'
```

That means each option:

- *wal_level* specifies the level for wal file creation. If you want archive them, you should put **archve** or **hot_standby**
- *max_wal_senders* specifies to how much replication connections is allowed (mainly used by **pg_basebackup**)
- *wal_keep_segments* specifies the minimum number of past log file segments kept in the pg_xlog directory.
- *archive_mode* activates the archive mode
- *archive_command* specifies a command for execute for archive one wal file.

Is strongly recommended archive wal files in different phisical disk and using commands that can guaranty the atomicity. A great example of bad command is using **scp**, beacuse it is not atomic.

The second step is allow replication connections, for it, you should enable them in **pg_hba.conf** file:

```text
local replication postgres trust
```

This assumes that replication connectons will be made from local. Replication connections in this case are used mainly by **pg_basebackup** tool.

Let start making a first complete standalone backup:

```text
pg_basebackup -D backupdir -U postgres -P -x -c fast -R
```

After executing that command, you should have in *backupdir* a complete santandalone backup.

You should keep all archived wal files that are created after backup. If something happens, and
you are forced to restore backup, you should follow the next steps:

- Restore the last base backup.
- Modify the recovery.conf file and add proper **restore_command** option (with something like: `'cp /mnt/archivedir/%f %p'` as value)
- Start the server.

When server going up, it will try apply all wal files found in the archive, making as a result the
completelly restored server.



