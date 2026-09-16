Works correctly: dry-run lists without removing, real run removes only aged dirs (including one with a space in its name — the old glob-based `ls`/word-splitting bug is gone), empty dirs are skipped, and a missing root exits with an error instead of silently `cd`-ing to the wrong place.

Files changed: `bin/clean-workspaces.sh`, `README.md`.
