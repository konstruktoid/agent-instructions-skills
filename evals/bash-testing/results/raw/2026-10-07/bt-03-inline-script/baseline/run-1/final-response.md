`bin/mkuser-config.sh` now rejects an empty `--name`. It prints `error: --name must not be empty` to stderr and exits 64, the same code the script uses for bad options. Nothing is written to the config. An omitted `--name` is rejected the same way.

The check is a few lines just before `mkdir -p` in `bin/mkuser-config.sh`. The new test is `bin/mkuser-config_test.sh`, which `make test` picks up. It covers the empty and omitted cases (non-zero exit, the message, no file written) and checks that a valid name still produces `alice:/bin/bash`.

`make test` passes with the fix. With the fix stashed, the new test fails with `FAIL: empty name exited 0`, so it does catch the bug.

A bare `--name` followed by another option, like `--name --out f`, still takes `--out` as the name, because the parser doesn't check that a value follows. I left that alone and didn't test it. I can tighten the parser if you want.

I haven't committed anything. The README says only `lib/` is covered by tests, which is now out of date. I didn't edit it.
