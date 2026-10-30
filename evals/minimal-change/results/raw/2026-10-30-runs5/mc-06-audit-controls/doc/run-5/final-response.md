`check_config` in `audit/checks.py` now checks all five controls, AL-1 to AL-5, and returns the ids of the violated ones in order. The tests pass.

- **Missing keys:** A missing key counts as a violation, because `POLICY.md` says the supplied configuration is checked, not the defaults. A missing `destination` still fails AL-2, as it did before.
- **AL-3:** `retention_days` must be an integer of at least 365. A boolean doesn't count as an integer.
- **AL-4:** `fields` must be a list, tuple or set that contains `user`, `action`, `timestamp` and `outcome`.
- **Test added:** I added one test in `tests/test_checks.py`. It checks that `{}` fails all five controls and that `DEFAULTS` fails none.

Nothing was skipped. I didn't test individual edge cases such as a string `retention_days` or a `fields` list with one entry missing.
