I extended `check_config` in `audit/checks.py` to cover AL-3, AL-4 and AL-5. I didn't run it or any tests.

- **AL-3:** it fails unless `retention_days` is an integer of at least 365. A boolean doesn't count as an integer, and a missing value fails.
- **AL-4:** it fails unless `fields` is a list, tuple or set that contains `user`, `action`, `timestamp` and `outcome`. A missing `fields` also fails.
- **AL-5:** it fails unless `tamper_protection` is `True`.

AL-1 and AL-2 are unchanged, and the ids still come back in order.
