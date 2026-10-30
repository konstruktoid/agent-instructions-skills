I added the AL-3, AL-4 and AL-5 checks to `check_config` in `audit/checks.py`. I haven't run it or written any tests.

- **AL-3:** fails unless `retention_days` is an integer of at least 365. A boolean doesn't count as an integer, and a missing value fails.
- **AL-4:** fails unless `fields` contains `user`, `action`, `timestamp` and `outcome`. A missing `fields` fails.
- **AL-5:** fails unless `tamper_protection` is exactly `True`.

The new checks come after AL-1 and AL-2, so failures are returned in order AL-1 to AL-5. I left the existing AL-1 and AL-2 checks as they were.
