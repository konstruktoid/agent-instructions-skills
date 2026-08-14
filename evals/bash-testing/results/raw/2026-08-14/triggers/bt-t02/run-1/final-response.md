This repo has no existing shell test framework — only one shell script (`scripts/backup.sh`) and a Python test suite (`tests/test_balance.py`, using plain pytest-style functions). There's no `test/`, `*.bats`, `test_*.sh`, Makefile test target, or CI test step for shell code.

Given that, here's where shell tests should go and what to call them:

- **Location**: mirror the existing Python convention and put them in `tests/`, alongside `test_balance.py`, rather than inventing a separate `test/` directory just for shell.
- **Framework/naming**: since there's no bats-core or shunit2 already vendored or referenced anywhere in the repo, the lowest-friction choice consistent with "match what's already there" is a plain test script — e.g. `tests/test_backup.sh` — that sources the testable parts of `scripts/backup.sh` and exits non-zero on failure, mirroring `test_balance.py`'s one-assertion-per-test style.
- If you'd rather adopt bats-core for shell specifically (nicer TAP output, `run`/`assert` helpers), that's a reasonable one-time choice too — it'd go in `tests/backup.bats`. But since nothing in the repo currently uses bats, I'd confirm that's what you want before introducing a second test framework.

One thing worth flagging: `scripts/backup.sh` currently runs everything at the top level (no functions, unquoted variables, backticks) — it isn't structured to be tested by sourcing. Adding real tests would first mean refactoring it into functions with a `main "$@"` entry point guarded by a `BASH_SOURCE` check, per the skill's testability step. Want me to do that refactor and add the first test?
