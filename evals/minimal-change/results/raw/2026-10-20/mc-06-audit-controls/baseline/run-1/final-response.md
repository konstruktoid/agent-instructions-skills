I extended `check_config` in `audit/checks.py` to cover AL-3, AL-4 and AL-5. It now returns the failing ids in order. I didn't run it or any tests.

- **AL-3:** `retention_days` must be an integer of at least 365. A missing value fails, and `True` or `False` don't count as integers.
- **AL-4:** `fields` must include `user`, `action`, `timestamp` and `outcome`. A missing `fields` fails.
- **AL-5:** `tamper_protection` must be `True`. A missing value fails.

I left the existing AL-1 and AL-2 checks unchanged. That means a missing `destination` still fails AL-2, because the code defaults it to `"stdout"`.
