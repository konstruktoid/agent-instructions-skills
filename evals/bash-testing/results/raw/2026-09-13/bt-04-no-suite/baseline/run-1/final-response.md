Verified: missing directory now exits 1 with a stderr message; a valid directory still prunes files older than the retention window (old.tar.gz deleted, new.tar.gz kept) and exits 0.

`bin/prune-artifacts.sh` is the only file changed.
