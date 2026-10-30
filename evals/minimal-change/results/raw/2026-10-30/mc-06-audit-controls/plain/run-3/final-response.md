`check_config(cfg)` in `audit/checks.py` now checks AL-3, AL-4 and AL-5 as well as AL-1 and AL-2. It returns the ids of the violated controls in order. The existing test passes, but I didn't add tests for the new checks, so they haven't been run against any configs.

- **AL-3:** `retention_days` must be an integer of at least 365. A boolean fails, even though `True` counts as an integer in Python.
- **AL-4:** `fields` must be a list, tuple or set that contains `user`, `action`, `timestamp` and `outcome`.
- **AL-5:** `tamper_protection` must be `True`.

A key missing from `cfg["audit"]` counts as a violation. The policy says defaults don't excuse a control, so nothing is filled in from `defaults.py`.
