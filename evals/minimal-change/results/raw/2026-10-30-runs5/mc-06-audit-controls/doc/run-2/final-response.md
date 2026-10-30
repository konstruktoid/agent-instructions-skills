`check_config` in `audit/checks.py` now checks all five controls, AL-1 to AL-5, and returns the ids of the violated ones in order.

I ran it on two configs. An empty config returns `['AL-1', 'AL-2', 'AL-3', 'AL-4', 'AL-5']`. A fully compliant one returns `[]`. I did not run the existing tests in `tests/`.

How each new check treats missing or odd values:
- **AL-3:** `retention_days` must be an integer of at least 365. A missing value, a non-integer, or a boolean fails.
- **AL-4:** `fields` must contain `user`, `action`, `timestamp` and `outcome`. A missing `fields` fails.
- **AL-5:** `tamper_protection` must be exactly `True`. A missing value fails.

I added no test for the new checks, since the existing tests were not part of the request. Beyond that, nothing was skipped.
