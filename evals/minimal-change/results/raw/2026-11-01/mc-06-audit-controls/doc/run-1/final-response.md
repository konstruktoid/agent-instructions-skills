`check_config` in `audit/checks.py` now checks all five controls and returns the ids of the ones that fail, in order. I ran it on two configs. An empty config returns `['AL-1', 'AL-2', 'AL-3', 'AL-4', 'AL-5']`. A fully compliant config returns `[]`.

AL-1 and AL-2 were already there. I added AL-3 to AL-5:
- **AL-3:** `retention_days` must be an integer of at least 365. A missing value, a non-integer, or a boolean fails.
- **AL-4:** `fields` must be a list, tuple or set containing `user`, `action`, `timestamp` and `outcome`. A missing value or a plain string fails, so a string like `"user action timestamp outcome"` can't pass by accident.
- **AL-5:** `tamper_protection` must be `True`.

I didn't add a test file, because the repo has no existing tests to match. I ran only the two ad hoc checks above.
