`bin/archive-logs.sh` now takes several service names, supports `--keep-days N`, and prints a one-line summary. I ran it against the sample `logs/` directory and the output matched what I expected.

**Usage:** `bin/archive-logs.sh [--keep-days N] SERVICE [SERVICE...]`

**What I tested:**
- **Archiving and pruning:** I put a 40-day-old file in `archives/`, then ran `--keep-days 30 api web`. Both new archives were created and the old one was removed.
- **Summary line:** it printed `archived 2 service(s): api web; pruned 1 archive(s) older than 30 days`. The "pruned" part only appears when you pass `--keep-days`.
- **Bad names:** an unknown service (`nope`) exits 1, and a path-like name (`../x`) exits 2, each with an error message.

I deleted the test archives afterwards, so `archives/` is empty again. I did not test `--keep-days` with an invalid value like `abc`, or a run where one archive fails partway.

**Behaviour to know about:**
- **Validation first:** all service names and the `--keep-days` value are checked before anything is archived. If one is bad, nothing is written.
- **Pruning order:** pruning runs only after every new archive is in place. It removes files in `archives/` named `*-YYYYMMDD.tar.gz` that are older than N days by modification time. That covers archives for any service, including ones made by hand with that naming.
- **Paths:** `logs/` and `archives/` are still relative to the current directory, as before, so cron needs to run it from the repo root. The README now says so.

**Other fixes:**
- The script now exits on any error (`set -euo pipefail`).
- Variables are quoted.
- The temp directory comes from `mktemp -d` and is cleaned up on exit.
- The tarball now stores paths as `SERVICE/...` instead of `logs/SERVICE/...`, because it runs `tar -C logs`. Anything that expects the old `logs/` prefix inside the archives would notice.

The README describes the new usage, the pruning rules, and the summary line.

I haven't committed anything.
