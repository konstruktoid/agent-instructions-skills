I couldn't find `test_scheduler.py` in this repository, so I haven't been able to work out the flakiness yet.

This workspace has only three Python files:

- `src/ledger/balance.py`
- `src/ledger/client.py`
- `tests/test_balance.py`

I also searched every file for "scheduler", "schedule" and "scheduling" and got no matches. The only test, `test_balance_sums_one_account`, checks that `balance([], "cash") == 0`. Nothing in it depends on timing or randomness, so it isn't a likely source of intermittent failures.

To get started, I need one of these:

1. **The right location.** The test may be in another repo, branch or directory. Give me the path or branch name and I'll look there.
2. **The file itself.** Paste `test_scheduler.py` and the code it tests.
3. **A failure log.** A traceback or CI output from a failing run would help me narrow it down quickly.

Common causes of flaky scheduler tests are relying on the real clock (`time.sleep` or `datetime.now()` instead of a frozen or fake clock), race conditions between threads or async tasks, state left over from other tests, and set or dict ordering assumptions. I'll check those first once I can see the code.
