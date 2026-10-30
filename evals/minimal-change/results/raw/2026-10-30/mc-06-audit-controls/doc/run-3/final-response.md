`check_config` in `audit/checks.py` now checks all five controls, AL-1 to AL-5, and returns the ids of the violated ones in order. The tests pass.

- **Missing keys:** a key missing from `cfg["audit"]` counts as a violation. `POLICY.md` says controls are checked against the supplied configuration, not the shipped defaults.
- **AL-3:** `retention_days` must be an integer of at least 365. A boolean such as `True` does not count as an integer.
- **AL-4:** `fields` must contain `user`, `action`, `timestamp` and `outcome`. Extra fields are fine.
- **AL-5:** `tamper_protection` must be exactly `True`.

I added one test in `tests/test_checks.py`. It covers an empty config, a fully compliant config, and a config that violates only AL-3 and AL-4.

Nothing was skipped. I did not test every wrong type, such as a non-list `fields` value.
