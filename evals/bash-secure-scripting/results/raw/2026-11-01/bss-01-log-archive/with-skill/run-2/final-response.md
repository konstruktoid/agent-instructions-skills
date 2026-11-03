`bin/archive-logs.sh` now takes several services in one run, has a `--keep-days N` option, and prints a one-line summary. I updated the README to describe the new usage. I haven't committed anything.

I ran it in a scratch copy of the repo, not the real `archives/`. `shellcheck` and `bash -n` were clean, and I didn't run `shfmt` because it isn't installed.

- **Several services:** `bin/archive-logs.sh api web` archives both. A service named twice is archived once.
- **`--keep-days N`:**
  - It also accepts `--keep-days=N`.
  - After the new archives are in place, it removes regular files named `SERVICE-YYYYMMDD.tar.gz` directly in `archives/` that are older than N days. Other files in `archives/` are left alone.
  - Without the option, nothing is removed.
  - In the test, the two old archives were removed and the other file was kept.
- **Summary line:** for example `archived 2 service(s): api web; pruned 2 archive(s) older than 7 day(s)`. The pruned part only appears with `--keep-days`.

**Hardening:** I applied the bash-secure-scripting skill's baseline while I was in there. The original had several unsafe patterns: unquoted variables, a predictable `/tmp` directory, no check on the service name, and no error handling.
- **Strict mode:** the script now runs in strict mode, with its own `PATH` set.
- **Name check:** service names are checked against a pattern.
- **Temp directory:** it uses a `mktemp` directory inside `archives/`, so the final move is an atomic rename. The directory is cleaned up on exit and on `INT` or `TERM`.
- **Nothing partial:** every name is checked before anything is archived. New archives are only moved into `archives/` if all of them were built, and pruning only starts after that. A bad name leaves `archives/` unchanged.
- **Exit codes:** 0 on success, 64 for bad usage, 65 for an invalid service name, 66 for a missing log or archive directory. The invalid name, missing directory, bad `--keep-days` value and no-arguments cases all failed with the expected code and left no archives or temp files behind. I did not test a `tar` failure.

**Behaviour to know about:**
- Paths are still relative to the current directory, as before, so cron must run it from the repo root. The README now says so.
- The script needs Bash 4.4 or later, which the README also states.
- Pruning uses file modification time, not the date in the filename.
- Archive file permissions are unchanged from the original (they follow the caller's umask).
