I extended `check_config` in `audit/checks.py` to cover AL-3, AL-4 and AL-5, alongside the existing AL-1 and AL-2 checks. I haven't run it or any tests.

- **AL-3:** it fails unless `retention_days` is an integer of at least 365. A missing value fails, and so does `True` or `False`, even though `bool` is technically an `int` in Python.
- **AL-4:** it fails unless `fields` contains all of `user`, `action`, `timestamp` and `outcome`. A missing or empty `fields` also fails.
- **AL-5:** it fails unless `tamper_protection` is `True`.

The ids come back in policy order.
