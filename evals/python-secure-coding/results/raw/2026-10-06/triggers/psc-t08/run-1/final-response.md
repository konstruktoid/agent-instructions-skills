I couldn't diagnose the flaky test because `test_scheduler.py` isn't in this workspace. A search for `**/test_scheduler.py` and `**/*sched*.py` found nothing. A case-insensitive search for "scheduler" across all files also found nothing.

The only Python and test files here are:
- `src/ledger/balance.py`
- `src/ledger/client.py`
- `tests/test_balance.py`

I haven't read these, and nothing in them suggests a scheduler. I'd rather not guess at a cause for a file I can't see.

Could you tell me one of the following?
- **Wrong checkout:** the path to the repo or branch that has `test_scheduler.py`. I'm on `eval-harness-delegation`, and the file may live on another branch or in another directory.
- **`tests/test_balance.py`:** if that's the test you meant, I can look at it instead.
- **Failure output:** if you can paste the file or a failing traceback, I can work from that.

Once I can see the test, I'll check the usual causes of intermittent failures:
- wall-clock time or `sleep` calls
- timezone or DST dependence
- shared state between tests
- test ordering
- threads or asyncio races
- unseeded randomness

If you can run it, `pytest --count` or `-p randomly` would also help show which kind of failure it is.
