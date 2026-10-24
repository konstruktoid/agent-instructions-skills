`check_config` in `audit/checks.py` now checks AL-3, AL-4 and AL-5 as well as AL-1 and AL-2. It returns the violated ids in order, and the tests pass.

- **AL-3:** `retention_days` must be an integer of at least 365. A missing value, `True` and `False` all fail.
- **AL-4:** `fields` must include `user`, `action`, `timestamp` and `outcome`. Extra fields are fine, and a missing `fields` key fails.
- **AL-5:** `tamper_protection` must be `True`.

The check reads only the config it is given and never falls back to `audit/defaults.py`, as `POLICY.md` requires. I added one test in `tests/test_checks.py`. It covers a compliant config, a config that fails AL-3 to AL-5, and the boolean case for retention.

I didn't test other bad types, such as `fields` being a string, since the policy doesn't say how to treat them.
