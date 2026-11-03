`bin/mkuser-config.sh` now rejects an empty or missing `--name`. It prints `error: --name must not be empty` to stderr, exits 64 (matching the script's existing usage-error code) and writes nothing. `make test` passes.

The new test is `bin/mkuser-config_test.sh`, which `make test` picks up automatically. It covers `--name ""`, a missing `--name` and a valid name (`bob`). For the two rejected cases it checks the non-zero exit, the message, and that the output file is still empty.

I didn't confirm that the test fails without the fix. I haven't committed anything.
