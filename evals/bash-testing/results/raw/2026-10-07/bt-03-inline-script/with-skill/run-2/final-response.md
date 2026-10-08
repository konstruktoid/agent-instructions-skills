`bin/mkuser-config.sh` now rejects an empty or missing `--name`. It prints `error: --name must not be empty` to stderr, exits 64 (the script's existing usage-error code), and writes nothing to the output file. `make test` passes, and `shellcheck` and `bash -n` are clean.

- **Fix:** the check runs after argument parsing and before `mkdir` and the append. Besides `--name ''`, it also catches the case where `--name` is left out entirely.
- **Test:** I added `bin/mkuser-config_test.sh`, a plain `*_test.sh` script like the existing `lib/format_test.sh`, which `make test` picks up. It checks the non-zero status, the stderr message, empty stdout and an untouched output file for both the empty and the missing name. It also checks that a valid name still appends `alice:/bin/sh`, using an `--out` path with a space in it.
- **Regression check:** I ran the new test before making the fix and it failed with "exit status 0 for empty name". It passes after the fix.
- **README:** I updated the coverage note, which said only `lib/` was covered.

I didn't commit anything.
