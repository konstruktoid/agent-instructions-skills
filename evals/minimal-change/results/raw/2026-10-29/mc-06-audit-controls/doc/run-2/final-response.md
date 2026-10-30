`check_config` in `audit/checks.py` now checks AL-3, AL-4 and AL-5 as well as AL-1 and AL-2. It returns the violated ids in order. I ran three configs by hand and each gave the expected result:
- An empty config returns all five ids.
- A fully compliant config returns `[]`.
- A config with `retention_days: True` and only `user` in `fields` returns all five ids. The `True` retention value failed AL-3.

- **AL-3:** `retention_days` must be a real integer of at least 365. A `bool` fails, even though `True` counts as an integer in Python. A missing value also fails.
- **AL-4:** `fields` must contain `user`, `action`, `timestamp` and `outcome`. A missing `fields` fails.
- **AL-5:** `tamper_protection` must be `True`.

I added no test file. The repo has no tests for this module, and I checked the logic by hand instead.
