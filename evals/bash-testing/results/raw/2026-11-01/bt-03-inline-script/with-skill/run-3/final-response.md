`bin/mkuser-config.sh` now rejects an empty `--name`. It prints `mkuser-config: --name must not be empty` to stderr, exits 64 (the same code the script already uses for bad options), and writes nothing. Omitting `--name` entirely is rejected the same way.

`make test` passes with the fix. I also ran the new test against the unfixed script, and it failed with "empty --name exited 0", so it does catch the bug.

The test is `bin/mkuser-config_test.sh`, a plain script that `make test` picks up. The repo already uses plain `*_test.sh` scripts, so I added no framework. It covers:
- **Empty name:** non-zero exit, the message on stderr, and no entry written.
- **Missing `--name`:** non-zero exit and nothing written.
- **Valid name:** still appends exactly one entry, using an output path that contains a space.

`bash -n` is clean on the test. `shellcheck` reports only an info-level SC1091 ("not following `lib/format.sh`") on the script, which is only because I didn't pass `-x`. I didn't run shellcheck on the new test file separately.

I haven't committed anything.
