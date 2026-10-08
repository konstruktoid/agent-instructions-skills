`bin/mkuser-config.sh` now rejects an empty or missing `--name`. It prints `error: --name must not be empty` to stderr, exits 64 (the same code as its unknown-option error) and writes nothing to the output file.

I added `bin/mkuser-config_test.sh`, which `make test` picks up. It covers four cases:
- **Empty name:** `--name ''` is rejected with the message and a non-zero exit, and no entry is written.
- **Missing name:** leaving out `--name` entirely is rejected with no entry written.
- **Valid name:** a normal name still writes `alice:/bin/bash`.
- **Regression check:** with the fix stashed, the test fails ("empty name exited 0"). With the fix, `make test` passes.

I also updated the README line saying only `lib/` is covered.

One separate bug I left alone: `--name` followed directly by another flag, as in `--name --out FILE`, takes `--out` as the name's value. That ends in an "unknown option" error rather than the new message.
