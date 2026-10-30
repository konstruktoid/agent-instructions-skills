I added AL-3, AL-4 and AL-5 to `check_config` in `audit/checks.py`, so it now covers all five controls in `POLICY.md`. I haven't run it or written any tests.

- **AL-3:** it fails unless `retention_days` is an integer of at least 365. A missing value fails, and so does `True`/`False`, which Python would otherwise count as integers.
- **AL-4:** it fails unless `fields` is a list, tuple or set containing `user`, `action`, `timestamp` and `outcome`. A missing `fields` also fails.
- **AL-5:** it fails unless `tamper_protection` is `True`. A missing value fails.

Ids come back in the order AL-1 to AL-5. I left the existing AL-1 and AL-2 checks as they were. That means a config with no `destination` is reported as violating AL-2, because the code treats a missing destination as `"stdout"`.
