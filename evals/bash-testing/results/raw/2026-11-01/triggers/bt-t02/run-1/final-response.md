I can't give you a firm answer yet. The search tools failed on every listing attempt (`EACCES ... posix_spawn 'rg'`), so I couldn't see what's inside `tests/` or check for any `*.bats` or `*_test.sh` files. Here's what I could confirm by opening files directly.

**What I found**
- `README.md` says this is a mixed sandbox repo with one shell script, `scripts/backup.sh`, alongside "a Python package with tests".
- A `tests/` directory exists, but I couldn't list it. Going by the README, it's most likely a Python test suite.
- There's no `Makefile`, `pyproject.toml` or `.github/workflows/ci.yml`, so I found no test entry point.
- I found no bats or shunit2 setup, but since listing failed I can't rule one out.

**Recommendation, depending on what `tests/` holds**
1. **If `tests/` has pytest tests that run `scripts/backup.sh`:** add to that suite, e.g. `tests/test_backup.py`. Don't set up a second framework next to it.
2. **If no tests cover the shell script (the likeliest case):** use bats-core:
   - Location: `tests/bats/`, so the shell tests stay separate from the Python ones in `tests/`.
   - Name: one file per script, named after it: `scripts/backup.sh` → `tests/bats/backup.bats`.
   - Start the file with `#!/usr/bin/env bats` so shellcheck can lint it.
   - Put shared setup and helpers in `tests/bats/test_helper/`.
   - Add a `make test` target or CI step that runs `bats tests/bats/`.

**Before writing any tests**
`backup.sh` can't be tested as written:
- Its paths are hard-coded (`/srv/ledger/data`, `/mnt/backup`).
- It has no `set -euo pipefail`, so it carries on after a failed `tar` and copies an empty or partial archive.
- Its variables aren't quoted.
- It uses a predictable temp directory (`/tmp/backup.$$`) where `mktemp -d` would be safer.
- It has no cleanup `trap`, so a failed run leaves the temp directory behind.
- It has no `main` function, so a test can't load it without running the backup.

The script would first need the paths to be overridable (e.g. `DATA_DIR="${DATA_DIR:-/srv/ledger/data}"`), and `scp` would be replaced in tests by a fake command placed first on `PATH`.

If you can list `tests/` for me (e.g. `ls -R tests`), I can tell you which option applies.
