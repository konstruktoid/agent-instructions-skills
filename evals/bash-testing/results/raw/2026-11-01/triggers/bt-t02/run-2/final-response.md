I couldn't confirm everything: the search tools failed in this environment (`rg` gave a permission error), so I couldn't list directory contents. Here's what I could check.

## What's in the repo

- **The only shell script is `scripts/backup.sh`.** There are no `.bats`, `*_test.sh` or `test_*.sh` files.
- **There's no shell test framework.** No `Makefile`, no `test/` directory, and no vendored bats or shunit2.
- **A `tests/` directory exists**, but I couldn't see inside it. The README says the repo has "a Python package with tests," so it's probably a pytest suite.
- **`.github/workflows/` exists**, but I couldn't read the files in it, so I don't know what the CI test step runs.

## Recommendation

**If `tests/` is pytest and you're fine adding a Python test,** put the backup tests there as `tests/test_backup_sh.py`, using `subprocess` to run the script. That keeps one test framework and one CI step instead of adding a second one beside it.

**If you want native shell tests,** use bats-core:

- **Location:** `test/` at the repo root, or `tests/shell/` if you'd rather keep a single tests tree.
- **Name:** one file per script, named after it: `scripts/backup.sh` → `test/backup.bats`.
- **Helpers:** `bats-support` and `bats-assert` in `test/test_helper/`, as git submodules or vendored copies.
- **Wiring:** add a `make test` target (or a CI step) that runs `bats test/`, and run `shellcheck` on the `.bats` files too.

## Before you write tests for `backup.sh`

As written, it's hard to test and has some real bugs:

- **Hard-coded paths and host.** `DATA_DIR`, `TARGET` and the scp host are fixed, so a test can't point it at a scratch directory. Make them overridable, e.g. `DATA_DIR="${DATA_DIR:-/srv/ledger/data}"`.
- **Nothing stops on failure.** It doesn't use `set -euo pipefail` or check exit codes, so it keeps going after a failed `tar` or `scp` and still exits 0.
- **Unsafe temp directory.** `/tmp/backup.$$` is a predictable name. Use `mktemp -d`, with a `trap` that removes it on exit.
- **No sourcing guard.** Its logic isn't in functions, so a test can't load it without running it. Wrap it in a `main` function guarded by `[[ ${BASH_SOURCE[0]} == "$0" ]]`.

Worth testing first:
- `scp` fails (stubbed through `PATH`) → the script exits non-zero.
- The temp directory is gone after both a successful and a failed run.
- A data directory whose path contains a space still works.

If you tell me which route you want (pytest or bats), I can set it up and write those tests.
