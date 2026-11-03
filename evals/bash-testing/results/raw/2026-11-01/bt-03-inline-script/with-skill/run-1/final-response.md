`bin/mkuser-config.sh` now rejects an empty `--name`. It prints `mkuser-config: --name must not be empty` to stderr and exits 64, the same code it already uses for unknown options. The check runs before anything is created, so no entry is appended and the output directory isn't made. Omitting `--name` entirely is rejected the same way.

I added `bin/mkuser-config_test.sh`, a plain-script test that follows the repo's `*_test.sh` convention. I didn't add a framework. It checks four things:
- **Empty `--name`:** non-zero exit, the message on stderr, nothing on stdout, and no config file written.
- **Missing `--name`:** the same rejection.
- **Spaced path:** the output path contains a space.
- **Valid name:** `alice` is still accepted and writes `alice:/bin/bash`.

`make test` passes with the fix. With the fix stashed it fails with `FAIL: empty --name exited 0`, so the test does catch the bug. `bash -n` is clean. `shellcheck` reports only an info-level SC1091 on the existing `source` line, which I left alone.

An invocation like `--name` as the last argument with no value is still not handled cleanly: `shift 2` fails under `set -e`. I didn't change that.
