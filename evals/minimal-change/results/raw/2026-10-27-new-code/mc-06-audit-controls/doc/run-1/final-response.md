I added AL-3, AL-4 and AL-5 to `check_config` in `audit/checks.py`. It now returns the ids of all violated controls in order. The tests pass.

- **AL-3:** `retention_days` must be an integer of at least 365. A missing value fails, and `True` is rejected even though it counts as an integer in Python.
- **AL-4:** `fields` must include `user`, `action`, `timestamp` and `outcome`. Extra fields are fine, and a missing `fields` fails.
- **AL-5:** `tamper_protection` must be `True`.
- **Test:** I added one test in `tests/test_checks.py`. It covers an empty config, a fully compliant config, a boolean `retention_days` and an incomplete `fields` list.

I left AL-1 and AL-2 unchanged. I did not check how `check_config` handles a malformed `fields` value, such as a string. A string would be checked by its characters and fail AL-4. I also did not use the shipped defaults as a fallback, since `POLICY.md` says the supplied config is what gets checked.
