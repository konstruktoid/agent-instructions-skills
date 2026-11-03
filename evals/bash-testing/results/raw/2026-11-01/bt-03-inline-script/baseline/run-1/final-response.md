`bin/mkuser-config.sh` now rejects an empty name. It prints `error: --name must not be empty` to stderr, exits 64 (the script's existing usage-error code), and writes nothing to the config. `make test` passes with the fix. With the fix stashed, the new test fails on `--name ""`.

- **Omitted name:** leaving out `--name` entirely is also rejected, since the name defaults to empty.
- **Trailing `--name`:** a bare `--name` as the last argument used to exit silently because `shift 2` failed under `set -e`. It now falls through to the same clear message.
- **Test:** `bin/mkuser-config_test.sh` is picked up by `make test`. It covers `--name ""`, a bare `--name`, and no `--name`, checking each for a non-zero exit, the message, and an untouched config file. It also checks that a valid name still writes `bob:/bin/bash`.

I didn't change `--name --out path`. There `--out` becomes the name and `path` is reported as an unknown option, which was already the behavior. I didn't commit anything.
