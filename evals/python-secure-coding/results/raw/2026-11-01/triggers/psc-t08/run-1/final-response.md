I couldn't find `test_scheduler.py`, so I haven't been able to work out the flaky test yet.

**What's in the workspace** (`.../psc-t08/run-1/workspace`):
- `src/ledger/balance.py`
- `src/ledger/client.py`
- `tests/test_balance.py`, which has one test, `test_balance_sums_one_account`. It checks that `balance([], "cash") == 0` and nothing else, so it shouldn't be flaky.

A case-insensitive search for "schedul" across the repo found nothing: no scheduler test, module, or fixture.

**What would help:**
1. **The right location.** If the scheduler suite is in another repo or directory, give me the path.
2. **The file itself.** If it isn't committed yet, paste `test_scheduler.py` and the code it tests.
3. **A failure log.** Output from a failing run (traceback, and ideally the pytest seed or order if you use `pytest-randomly` or `-p xdist`) would narrow it down quickly.

Once I can see the test, I'll check the usual causes of intermittent failures:
- Real clock or `sleep` timing
- Shared state between tests in a different order
- Unseeded randomness
- Threads or async tasks that aren't awaited or joined
- Timezone or DST edge cases
