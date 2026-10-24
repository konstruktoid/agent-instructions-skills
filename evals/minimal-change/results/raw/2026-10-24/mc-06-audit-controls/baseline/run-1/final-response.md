I extended `check_config` in `audit/checks.py` to cover AL-3, AL-4 and AL-5. It now returns the ids of all violated controls in order. I haven't run it or added tests.

- **AL-3:** `retention_days` must be an integer of at least 365. A missing value, a non-integer, or a boolean fails.
- **AL-4:** `fields` must be a list, tuple or set containing `user`, `action`, `timestamp` and `outcome`. A missing `fields` fails.
- **AL-5:** `tamper_protection` must be exactly `True`.

I left the existing AL-1 and AL-2 checks as they were.
