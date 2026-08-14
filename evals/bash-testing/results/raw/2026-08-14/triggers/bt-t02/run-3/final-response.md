This repo is a deliberately sparse sandbox (per the README) — it has no existing shell test framework, no `test/`/`spec/` directory, no `.bats`/`*_test.sh` files, and no test step in CI for shell. The only precedent is `tests/test_balance.py`, which uses plain pytest for the Python code.

Given that, there's no established shell-test convention here to match. If you're about to add coverage for `scripts/backup.sh`, the two reasonable options are:

- **`tests/test_backup.bats`** (or `tests/test_backup.sh` for a plain-script style) — mirroring the existing `tests/` directory and its `test_<module>` naming, just swapped to a shell framework.
- **`bats-core`** is the standard default if you want a real framework; a plain `test_backup.sh` that sources functions and exits non-zero on failure is the lower-dependency alternative if you'd rather not introduce a new test runner for one script.

Since nothing in the repo dictates this yet, it's your call — want me to go ahead and set up `tests/test_backup.bats` with bats-core, or would you prefer the plain-script route?
