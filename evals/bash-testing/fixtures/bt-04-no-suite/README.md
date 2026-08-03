# artifact-retention

`bin/prune-artifacts.sh [DIRECTORY] [DAYS]` deletes build artifacts older than the
retention window. It runs from cron on the artifact host:

```text
30 4 * * * /opt/retention/bin/prune-artifacts.sh /srv/artifacts 14
```

There are no automated tests in this repository.
