I couldn't find `test_scheduler.py` in this repo, so I haven't found the cause of the flaky test yet.

What's in the workspace:

- `src/ledger/balance.py`
- `src/ledger/client.py`
- `tests/test_balance.py`

I also searched every file for "schedul" and got no matches. So there's no scheduler test or scheduler code here. The only test is `tests/test_balance.py:6`, which checks that `balance([], "cash") == 0`. It has no timing, randomness or shared state, so it isn't the flaky one.

Possible explanations:

1. The test is on a branch or in a commit that isn't checked out here.
2. It's in a different repo or directory than this workspace.
3. The file has a different name.

If you tell me where it lives, or paste the test, the code it covers, and an example failure, I'll dig in. The usual causes worth checking are:

- timing assumptions, like `sleep`, wall-clock comparisons or timeouts
- state shared between tests through globals or fixtures with the wrong scope
- tests that depend on run order, which `pytest -p random_order` can expose
- unseeded randomness
- threads or async tasks that aren't awaited or joined
