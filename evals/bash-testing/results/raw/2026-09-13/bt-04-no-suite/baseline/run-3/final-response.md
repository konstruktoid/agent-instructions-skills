Verified: existing directory still prunes correctly and exits 0 (old.tar.gz removed, new.tar.gz kept), and a missing/mistyped path now exits 1 with an error on stderr instead of silently exiting 0.

**Changed:** `bin/prune-artifacts.sh`
