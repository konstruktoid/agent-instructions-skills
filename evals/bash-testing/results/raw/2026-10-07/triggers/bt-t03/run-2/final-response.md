I couldn't find an input validation script, so I haven't written any tests.

- **The only shell script is `scripts/backup.sh`.** It takes no arguments and reads no input. It has no empty-value or length check, so it has no rejection paths to cover.
- **Nothing else matches.** I searched the whole repository for validation logic (`valid`, length checks, `-z` tests) and found none.
- **The tests that exist are Python.** `tests/test_balance.py` is the only test file, and it covers `ledger.balance`. There is no bats or shunit2 suite, and no `Makefile`.

Which script did you mean? It may be on another branch or not committed yet. If you give me its path, I'll write the tests to match this repository's layout.

If you meant `backup.sh`, tell me and I'll cover it instead. It would need some changes first, because it has no argument handling and no guard for sourcing it in a test. Its other weak spots are unquoted variables, no check that `mkdir` or `tar` succeeded, and no cleanup if a step fails. I'd rather not invent validation rules for it without your say-so.

Separately, `.github/workflows/deploy.yml` has `permissions: write-all`. It also interpolates the pull request title straight into a `run:` step, which allows script injection. I left it alone since it's outside this request.
