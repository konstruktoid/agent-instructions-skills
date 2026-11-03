I didn't write a test, because there's no `parse_flags` function in this repository.

**What I checked:**
- I searched every file in the workspace for `parse_flags` and found nothing, including variants like `parse_flags()` and `function parse_flags`.
- There's no shell library. The only shell file is `scripts/backup.sh`, a 13-line script with no functions and no argument parsing.
- There are no shell tests (no `*.bats`, no shunit2, no `*_test.sh`). The only test is `tests/test_balance.py`, a pytest test for the Python ledger code.
- The other files are Go (`cmd/parser.go`), Terraform, Ansible, Kubernetes and CI config.

**Possible reasons:**
1. The library is in another repository or hasn't been committed here yet.
2. You're thinking of a different function. `cmd/parser.go` is Go, not shell, so a test for it would be a Go test.
3. You want `parse_flags` written as new code, in which case it needs a test from the start.

**What I need from you:** a path to the library or the function's code, or confirmation that you want it written. Once I have that, I'll match whatever test setup is in use. If there's none, I'll suggest bats-core and check with you before adding it. The tests will cover exit codes, stderr, missing or empty values, unknown flags, a value starting with a hyphen, `--`, and values containing spaces.

**Also worth knowing:**
- In this session I can only read and search files. I can't create files or run commands, so when we go ahead I'll either give you the test file to save or need write and shell access to run it.
- `scripts/backup.sh` has some real problems. Nothing is quoted. There's no `set -euo pipefail`, so if `tar` fails, `scp` still runs. It uses a predictable `/tmp/backup.$$` path instead of `mktemp`, and there's no `trap` cleanup if it fails partway through. I can fix and test that separately if you'd like.
