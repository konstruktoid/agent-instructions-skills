`check_config` in `audit/checks.py` now checks all five controls, AL-1 to AL-5, and returns the ids of the violated ones in order. Both tests pass.

- **Defaults:** missing keys count as violations. `POLICY.md` says to check the supplied config, not the shipped defaults, so `check_config({})` returns all five ids.
- **AL-3:** `retention_days` must be an integer of at least 365. A `bool` is rejected, even though Python treats `True` as an integer.
- **AL-4:** `fields` must contain `user`, `action`, `timestamp` and `outcome`. Extra fields are fine.
- **Tests:** I added one test to `tests/test_checks.py` covering AL-3 to AL-5, plus the all-missing case.

I did not add checks for malformed shapes, such as `fields` being a non-list or `audit` not being a dict.
