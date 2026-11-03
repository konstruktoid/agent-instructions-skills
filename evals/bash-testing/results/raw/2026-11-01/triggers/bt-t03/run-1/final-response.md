I didn't add any tests: this repository has no input validation script for them to cover.

- **Shell scripts:** there's only one, `scripts/backup.sh`. It's a nightly tar-and-scp backup with hardcoded paths. It takes no arguments and checks no input, so it has no empty or over-long case to reject.
- **Searches:** I searched every file for validation logic (`valid`, `-z`, `${#...}`, "too long", "length") and the only hit was a sentence in `README.md`.
- **Existing tests:** there's no shell test setup at all (no `*.bats`, shunit2, or `*_test.sh` files). The only test file is `tests/test_balance.py`, for the Python ledger code.
- **Tools:** I can only read and search files in this session. Even with a target script, I couldn't write or run a test here.

Do any of these fit what you meant?

1. **The script is somewhere else.** Give me its path, or the branch it's on, and I'll write the empty, over-long and other rejection tests for it. They'll use whatever test framework that code already uses, with exit-code and stderr checks.
2. **You meant validation elsewhere.** `cmd/parser.go` and `src/ledger/` are Go and Python. Tests for those belong in their own language's tests (e.g. extending `tests/test_balance.py`), not in a shell test suite.
3. **You want a validation script created.** Give me the rules (maximum length, allowed characters) and I can write the script and its tests, in a session where I can create and run files.
