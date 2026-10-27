I added the AL-3, AL-4 and AL-5 checks to `check_config` in `audit/checks.py`. I haven't run it or tested it.

- **AL-3:** it fails unless `retention_days` is an integer of at least 365. A missing value fails, and `True` doesn't count as an integer.
- **AL-4:** it fails unless `fields` contains `user`, `action`, `timestamp` and `outcome`. A missing `fields` fails.
- **AL-5:** it fails unless `tamper_protection` is `True`. A missing value fails.

The ids come back in order AL-1 to AL-5. I left the existing AL-1 and AL-2 checks as they were. AL-2 still treats a missing `destination` as a violation, which fits the policy's rule that defaults don't count.
