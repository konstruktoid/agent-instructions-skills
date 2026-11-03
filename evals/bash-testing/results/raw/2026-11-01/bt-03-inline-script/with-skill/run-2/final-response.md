`bin/mkuser-config.sh` now rejects an empty `--name`. It prints `error: --name is required and must not be empty` to stderr and exits 64, the same code it uses for an unknown option. It does this before creating the output directory or writing anything. An omitted `--name` is rejected the same way, since `name` defaults to empty.

I added `bin/mkuser-config_test.sh`. It follows the repo's plain `*_test.sh` convention, and `make test` picks it up. It checks:
- **Empty name:** non-zero exit, a message that mentions `--name`, and nothing written to the output file.
- **Omitted name:** the same three checks.
- **Output path:** the rejection tests use an `--out` path containing a space.
- **Valid name:** `alice` still produces `alice:/bin/bash`.

`make test` passes with the fix. With the fix stashed, it fails with `FAIL: empty: exited 0`, so the test does catch the bug. `shellcheck -x` and `bash -n` are clean.

I noticed one other problem and left it alone. A bare `--name` followed by another flag, such as `--name --out file`, takes `--out` as the name. That is an argument-parsing issue separate from this fix, and the test doesn't cover it.

I haven't committed anything.
