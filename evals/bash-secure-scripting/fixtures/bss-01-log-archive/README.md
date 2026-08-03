# ops-logtools

Small operations repository for the log retention job.

`bin/archive-logs.sh SERVICE` packs the logs of one service from `logs/` into a dated
tarball under `archives/`. It runs from cron on the log host every night.

Archives are pruned by hand today.
