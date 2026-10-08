`bin/mkuser-config.sh` now rejects an empty `--name`. It prints `mkuser-config: --name must not be empty` to stderr and exits 64, the same code it uses for unknown options. It exits before creating the output directory or appending anything. Omitting `--name` entirely hits the same check.

I added `bin/mkuser-config_test.sh`, a plain `*_test.sh` script like the existing `lib/format_test.sh`, so `make test` picks it up. It checks four things:
- **Empty `--name`:** it exits non-zero, writes a message to stderr, writes nothing to stdout, and leaves no entry in the output file.
- **Missing `--name`:** it gets the same rejection.
- **Valid name:** it still writes `alice:/bin/bash`.
- **Output path with a space:** the valid-name run uses one.

Before the fix, `make test` failed on "empty --name exited 0". After the fix, `make test` passes, and `shellcheck` and `bash -n` are clean.

The README says only `lib/` is covered by tests, which is no longer true. I didn't edit it. I haven't committed anything.
