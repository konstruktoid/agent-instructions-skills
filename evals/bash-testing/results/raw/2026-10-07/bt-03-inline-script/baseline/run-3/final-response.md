`bin/mkuser-config.sh` now rejects an empty name: it prints `error: --name must not be empty` to stderr, exits 64, and writes nothing to the config. `make test` passes with the fix. With the script change stashed, the new test fails, so it does catch a regression.

- **Script change:** the check sits after argument parsing, so `--name ""`, a missing `--name` and a bare trailing `--name` are all rejected. I also changed the `--name` branch so a bare trailing `--name` reaches the new message. Before, `shift 2` failed silently under `set -e`, so it exited non-zero with no message.
- **Missing `--name`:** this already exited 0 before the change and appended `:/bin/bash` to the config. It is now rejected too. Only `--name ""` and a bare trailing `--name` are in the test, not a missing `--name`.
- **Test:** I added `bin/mkuser-config_test.sh`, which `make test` picks up automatically. It checks that `--name ""` and a bare `--name` each give a non-zero exit, the message, and no output file content. It also checks that `--name alice` still writes `alice:/bin/bash`.
- **README:** it says "Only `lib/` is covered today", which is no longer true. I left it unchanged.

I haven't committed anything.
