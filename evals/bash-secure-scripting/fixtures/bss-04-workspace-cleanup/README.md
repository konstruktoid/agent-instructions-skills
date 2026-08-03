# ci-maintenance

Housekeeping scripts for the CI workers.

`bin/clean-workspaces.sh` removes stale build workspaces under `workspaces/`. The root and
the age threshold are hardcoded, so a worker with a different layout needs its own copy of
the script.
