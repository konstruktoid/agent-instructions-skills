I added AL-3, AL-4 and AL-5 to `check_config` in `audit/checks.py`. It now checks all five controls and returns the failing ids in order. I haven't run it or any tests.

- **AL-3:** `retention_days` must be an integer of at least 365. A missing value fails, and so does `True`, even though Python treats it as an integer.
- **AL-4:** `fields` must contain `user`, `action`, `timestamp` and `outcome`. A missing or non-collection `fields` fails.
- **AL-5:** `tamper_protection` must be exactly `True`. A missing value fails.

I left the existing AL-1 and AL-2 checks as they were. A missing `destination` still counts as an AL-2 violation, because the old code treats it as `"stdout"`. That fits the policy line that defaults are still checked against the supplied config.
