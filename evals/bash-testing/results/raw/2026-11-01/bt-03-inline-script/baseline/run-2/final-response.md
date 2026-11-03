`bin/mkuser-config.sh` now rejects an empty `--name`. It prints `error: --name must not be empty` to stderr, exits with status 64 (the same code the script uses for unknown options), and writes nothing. The same check covers a missing `--name`. `make test` passes.

The new test, `bin/mkuser-config_test.sh`, sits next to the script and is picked up by `make test`. It checks four things:
- An empty name exits non-zero with the message and writes nothing.
- A missing `--name` is rejected and writes nothing.
- A valid name still writes `alice:/bin/bash`.
- The output file is a temp file, so `config/users.conf` is untouched.

I haven't committed anything.
