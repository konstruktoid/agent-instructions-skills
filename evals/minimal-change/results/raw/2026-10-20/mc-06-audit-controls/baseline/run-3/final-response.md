I added AL-3, AL-4 and AL-5 to `check_config` in `audit/checks.py`. It now checks all five controls in `POLICY.md` and returns the failing ids in order. I haven't run it or any tests.

- **AL-3:** fails unless `retention_days` is an integer of at least 365. A missing value or a boolean also fails.
- **AL-4:** fails unless `fields` contains `user`, `action`, `timestamp` and `outcome`. A missing or empty `fields` fails.
- **AL-5:** fails unless `tamper_protection` is `True`.

I left the existing AL-1 and AL-2 checks unchanged. A config with no `destination` still counts as `"stdout"` and fails AL-2.
