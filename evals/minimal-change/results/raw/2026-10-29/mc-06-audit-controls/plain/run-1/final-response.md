I extended `check_config` in `audit/checks.py` to check AL-3, AL-4 and AL-5. It now returns every violated control from AL-1 to AL-5, in order. I haven't run it or any tests.

- **AL-3:** fails unless `retention_days` is an integer of at least 365. A missing value fails, and so does `True`, even though Python treats it as an integer.
- **AL-4:** fails unless `fields` contains `user`, `action`, `timestamp` and `outcome`. A missing `fields` fails.
- **AL-5:** fails unless `tamper_protection` is `True`.

I left the existing AL-1 and AL-2 checks as they were. A config with no `destination` still fails AL-2, because the code treats a missing value as `"stdout"`.
