I added AL-3, AL-4 and AL-5 to `check_config` in `audit/checks.py`. It now returns the violated control ids in order, and the tests pass.

- **AL-3:** Fails unless `retention_days` is an integer of at least 365. A boolean doesn't count as an integer.
- **AL-4:** Fails unless `fields` contains `user`, `action`, `timestamp` and `outcome`. A missing `fields` key counts as a violation.
- **AL-5:** Fails unless `tamper_protection` is `True`.

Missing keys count as violations. `POLICY.md` says controls are checked against the supplied config, not the shipped defaults, so `check_config` doesn't fall back to `DEFAULTS`.

I added one test in `tests/test_checks.py` covering AL-3, AL-4 and AL-5 together. I didn't add separate tests for each edge case, such as a boolean `retention_days` or a missing `fields` key.
