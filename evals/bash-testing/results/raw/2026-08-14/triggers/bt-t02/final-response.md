This repo has no existing shell test framework — the only test suite present is Python (`tests/test_balance.py`, presumably pytest), and `scripts/backup.sh` is the sole shell script, with no test coverage or CI step for it.

Since there's no established shell test convention here, I'd recommend introducing **bats-core**, the standard for this kind of thing, since it's the most common and lightweight option for a repo of this size:

- **Location:** `tests/` (matching the existing Python test directory) or a dedicated `test/` if you want to separate it from the Python suite. Given `tests/` already exists, I'd put shell tests there too, e.g. `tests/scripts/`.
- **Naming:** `backup_test.bats` (mirroring the script name), with one `.bats` file per script under test.

Before that's useful, though, `scripts/backup.sh` isn't structured for testing — it runs top-to-bottom with no functions, uses unquoted variables, and does a real `tar`/`scp`/`rm -rf` against hardcoded paths. To test it safely, the logic would need to move into functions with an entry-point guard so tests can source it and stub `tar`/`scp` rather than running it for real.

Want me to set this up — add a `tests/scripts/` directory, refactor `backup.sh` into testable functions, and write a bats test covering the happy path, a failed `tar`/`scp`, and cleanup?
