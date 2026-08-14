This repo is a deliberately mixed sandbox (per README.md) with no existing shell test framework — `scripts/backup.sh` is the only shell script, `tests/` currently holds only a pytest-style Python test, and the CI workflow doesn't run tests at all. So there's no established shell test convention to match.

Given a blank slate, the standard convention (per bats-core, the most common Bash test framework) would be:

- **Location:** `tests/`, alongside the existing Python tests — repos rarely split shell tests into a separate top-level directory unless they grow large. If you want them clearly separated from the Python suite, `tests/bash/` also works.
- **Naming:** `test_backup.bats` (or `backup.bats`) for a bats-core test targeting `scripts/backup.sh`. Bats' convention is `<name>.bats`, mirroring the script name, similar to how `test_balance.py` mirrors `balance.py`.
- **Runner:** since there's no `Makefile` or test step in CI yet, you'd also need to add one (e.g., `bats tests/` invoked from a CI step) for tests to actually run anywhere.

If you'd like, I can set this up — add `tests/test_backup.bats`, install/reference bats-core, and wire a test step into `.github/workflows/deploy.yml` (or a new workflow) so it actually runs. Want me to do that?
