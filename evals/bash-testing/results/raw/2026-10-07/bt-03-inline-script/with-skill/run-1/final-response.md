`bin/mkuser-config.sh` now rejects an empty `--name`. It prints `mkuser-config: --name must not be empty` to stderr, exits 64 (the script's existing usage-error code) and writes nothing. Omitting `--name` entirely is rejected the same way. `make test` passes with the fix, and `shellcheck -x` is clean on the script and the new test.

I added `bin/mkuser-config_test.sh`, a plain-script test like the existing `lib/format_test.sh`, which `make test` picks up automatically. It checks:
- **Empty name:** non-zero exit, the message on stderr, and no output file created.
- **Missing name:** same rejection as an empty one.
- **Valid name:** still writes `alice:/bin/bash`. This case uses an output path containing a space.

I confirmed the rejection test fails against the unfixed script ("empty --name exited 0") and passes with the fix.
