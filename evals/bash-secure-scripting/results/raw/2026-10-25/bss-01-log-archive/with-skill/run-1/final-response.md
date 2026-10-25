`bin/archive-logs.sh` now takes several service names and an optional `--keep-days N`, and prints one summary line. The README describes the new usage. I tested it in a scratch copy, not against the real `logs/` and `archives/`. `shellcheck` and `bash -n` are clean.

- **Usage:** `bin/archive-logs.sh [--keep-days N] SERVICE [SERVICE...]`.
- **Validation:** every service name is checked against `^[a-z0-9][a-z0-9_-]{0,63}$` before anything is archived. This stops names like `../x` or `a;b` from reaching `tar` or a path. Repeated names are archived once.
- **Pruning:** `--keep-days N` deletes archives older than N days by mtime, after the new archives are in place. It only touches files named `*-YYYYMMDD.tar.gz` directly in `archives/`, so hand-placed files are left alone. N must be a positive integer.
- **Summary:** for example `archived 2 service(s): web api; pruned 1 archive(s) older than 30 day(s)`. The `pruned` part appears only with `--keep-days`.
- **Failures:** if any service fails to archive, the script exits 1 and prunes nothing, so a bad night can't delete the old archives. Usage errors exit 64, and invalid values exit 65.
- **Hardening of the old script:**
  - It now has strict mode and a fixed `PATH`.
  - The predictable `/tmp/archive-logs.$$` directory is gone. It builds each tarball in a `mktemp -d` directory inside `archives/` and moves it into place, with cleanup on exit and on INT/TERM.
  - The old `rm -rf $TMP/*` is gone.

I ran multiple services, duplicates, pruning, a missing service, a bad name, a bad `--keep-days`, no arguments and a missing option value. Each gave the expected output and exit code, and no temp directories were left behind. I didn't test signal handling.

Things that behave differently from before:
- Pruning covers all services' archives in `archives/`, not just the ones named on that run. The README says so.
- Archives are now created with umask 027, so they are no longer world-readable.
- The script needs Bash 4.4 or later and GNU `find` and `tar`. I added `shopt -s inherit_errexit` for this.
- It prints one summary line, where it used to print `archived SERVICE` per service.
- It still uses the relative `logs` and `archives` paths, so cron must keep running it from the repository directory.

I haven't committed anything.
