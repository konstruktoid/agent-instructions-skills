I extended `bin/archive-logs.sh` to take several services and a `--keep-days N` option, and it now prints a one-line summary. I updated the README to match. I checked it in a scratch copy of the repo, not on the real `archives/`, and everything behaved as expected.

**What I ran**
- `shellcheck -x` and `bash -n` are clean. The repo has no `shfmt` config and `shfmt` isn't installed, so I didn't run a formatter.
- In the scratch copy, `web api --keep-days 30` archived both services and removed a 40-day-old archive. It left `keep.txt` alone and printed `archived 2 service(s): web api; pruned 1 archive(s) older than 30 day(s)`.
- Four bad inputs failed as intended:
  - A service with no log directory exits 1.
  - `../x` as a service name exits 64.
  - A non-numeric `--keep-days` value exits 64.
  - No arguments exits 64.
- No temp directory was left behind after any of those runs.

**How it behaves**
- **Several services:** you list them in one call, e.g. `bin/archive-logs.sh web api`. Names must match `[a-z0-9][a-z0-9_-]*`, and every name is checked before anything is archived.
- **`--keep-days N`:** pruning runs only after every new archive is in place, and if any archive fails nothing is deleted. Without the option nothing is ever deleted.
- **Summary line:** the `pruned` part appears only when `--keep-days` is given.

**Other changes**
- Paths now resolve relative to the repo (the parent of `bin/`), not the current directory. The old script depended on cron starting in the repo root.
- The script sets its own `PATH` and `umask`, uses `mktemp` inside `archives/`, and cleans up on exit and on `INT`/`TERM`. The old version used a predictable `/tmp` path and left `$TMP` behind.
- Tarballs now hold `web/...` rather than `logs/web/...`. Anything that reads the old archives by their internal paths would notice.

**Things to know**
- `--keep-days` prunes every `*-YYYYMMDD.tar.gz` file in `archives/`, not only the services named in that run. The README says this.
- Running twice on the same day overwrites that day's archive.
- The script now needs Bash 4.4+ and GNU `find` and `tar`.
- The changes are uncommitted.
