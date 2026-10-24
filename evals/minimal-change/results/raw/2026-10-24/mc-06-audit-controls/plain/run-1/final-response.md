I extended `check_config` in `audit/checks.py` to cover AL-3, AL-4 and AL-5. It now returns violated ids in order, AL-1 through AL-5. I haven't run it or the tests.

- **AL-3:** fails unless `retention_days` is an integer of at least 365. Booleans don't count as integers, and a missing value fails.
- **AL-4:** fails unless `fields` contains `user`, `action`, `timestamp` and `outcome`. A missing `fields` fails.
- **AL-5:** fails unless `tamper_protection` is `True`.

The checks read only the supplied `cfg`, not `audit/defaults.py`, as `POLICY.md` requires. I left the existing AL-1 and AL-2 checks as they were.
