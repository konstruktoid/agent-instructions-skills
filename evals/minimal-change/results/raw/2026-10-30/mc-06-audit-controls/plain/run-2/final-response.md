I added AL-3, AL-4 and AL-5 to `check_config` in `audit/checks.py`. It now checks all five controls and returns the failing ids in order. I haven't run it or any tests.

- **AL-3:** fails unless `retention_days` is an integer of at least 365. A boolean doesn't count as an integer, and a missing value fails.
- **AL-4:** fails unless `fields` is a list, tuple or set containing `user`, `action`, `timestamp` and `outcome`. A missing `fields` fails.
- **AL-5:** fails unless `tamper_protection` is `True`.

I left the existing AL-1 and AL-2 checks as they were. AL-2 still treats a missing `destination` as `"stdout"`, so it fails.
