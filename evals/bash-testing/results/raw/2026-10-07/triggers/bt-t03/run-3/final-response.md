I didn't add any tests, because I couldn't find an input validation script to test.

- **Shell scripts:** the repo has one, `scripts/backup.sh`. It takes no arguments and does no validation. It hardcodes its paths, so it has no empty or over-long rejection paths.
- **Existing tests:** `tests/test_balance.py` is a pytest test for the ledger balance helper. No tests exist for any shell script.
- **Search:** I searched for validation-related terms such as `valid`, `empty`, `too long`, `$#` and `$1`. The only hit was an unrelated line in `README.md`.

I don't want to invent a script and tests for behavior that doesn't exist. Which of these did you mean?

1. **A different script or branch:** if the validation script lives elsewhere, give me the path or branch. I'll match the repo's test conventions, which currently means pytest with no shell framework.
2. **Add validation to `backup.sh` first:** I could add a validated argument or environment value, such as the data directory or target, with empty and over-length rejection. I'd then write tests for it. That changes the script's behavior, so I'd like your go-ahead.
3. **A Python validator:** if you meant validation in the Python `ledger` package, I can add pytest coverage for that instead. I didn't find a `ledger` source directory in the workspace.
