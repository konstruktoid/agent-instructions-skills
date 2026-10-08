I haven't written the test yet. I can't tell which bug you fixed, and this session has no shell, so I can't run anything.

**What I found**
- The repo has `src/ledger/` (`balance.py`, `client.py`) and one test file, `tests/test_balance.py`.
- That test is a plain function with a docstring, with no fixtures and no config files. I'd match it with `tests/test_client.py`, importing `from ledger.client import get`.
- `client.py` has no visible bug marker. The checked-out code looks like the fixed version, but I couldn't see the diff or the git history to confirm that.

**Why that blocks the test**
A regression test has to fail on the old behavior, and that depends on what the old behavior was. Here are the likely candidates and the test each would need:

| Likely old bug | Test that fails on it |
|---|---|
| Truthiness check (`if result:`) instead of `is not None`, so a valid empty response `""` was retried | Transport returns `""` once, and the test asserts one call and a result of `""` |
| Wrong retry count (for example `MAX_ATTEMPTS - 1` calls) | Transport always returns `None`, and the test asserts exactly `MAX_ATTEMPTS` calls |
| Retry stopped after a success, or didn't retry after a failure | Transport returns `None` then `"ok"`, and the test asserts `"ok"` after two calls |

**What I need from you**
Which of these was the bug, or what did the diff change? If you'd rather not say, run `git diff <fix-commit>^ <fix-commit> -- src/ledger/client.py` and paste it here.

Once I know, I'll write the test with a counting fake transport and no mocking library, to match the existing style. To prove it fails without the fix, someone needs to revert the fix and run `pytest`. I can't run it in this session, so I'll give you the exact command.
