I extended `check_config` in `audit/checks.py` to cover AL-3, AL-4 and AL-5. It now returns the failing ids in order, AL-1 through AL-5. I haven't run it or any tests.

- **AL-3:** fails unless `retention_days` is an integer of at least 365. A missing value fails, and `True` doesn't count as an integer.
- **AL-4:** fails unless `fields` contains `user`, `action`, `timestamp` and `outcome`. A missing or empty `fields` fails.
- **AL-5:** fails unless `tamper_protection` is `True`.

I left the existing AL-1 and AL-2 checks as they were. AL-2 still treats a missing `destination` as `"stdout"`, so it fails.
