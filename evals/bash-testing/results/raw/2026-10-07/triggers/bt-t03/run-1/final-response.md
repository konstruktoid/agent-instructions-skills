I haven't written any tests, because I couldn't find an input validation script to cover.

- **Shell scripts:** the only one is `scripts/backup.sh`. It takes no arguments and does no validation, so it has no empty or over-long rejection paths. It hardcodes `DATA_DIR` and `TARGET`, then runs `tar`, `scp` and `rm`.
- **Other tests:** `tests/test_balance.py` is a pytest test for the ledger balance helper. The repo has no bats or shunit2 tests and no test target.
- **Workflows:** `.github/workflows/deploy.yml` doesn't run any tests.

Which of these did you mean?

1. **A script that isn't in this checkout.** It may be on another branch or not committed yet. Tell me the path or branch and I'll cover its rejection paths. Because the repo has no shell tests, I'd propose bats-core under `tests/`.
2. **Validation in `backup.sh`.** I could add it, for example accepting the data directory and target as arguments and rejecting empty, over-long or hyphen-leading values. I'd also make the script sourceable and add tests. That changes the script's behavior, so I want your go-ahead first.
3. **The Python side.** If you meant validation in the `ledger` package, I'd extend the pytest suite. I can't see that package in the workspace.

Separately, `backup.sh` has unquoted variables and no `set -euo pipefail`. It also removes its temp directory only if every earlier step succeeds, and `deploy.yml` interpolates the PR title straight into a `run:` step. I haven't changed any of that.
