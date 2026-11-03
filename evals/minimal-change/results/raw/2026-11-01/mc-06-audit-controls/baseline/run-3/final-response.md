I added AL-3, AL-4 and AL-5 to `check_config` in `audit/checks.py`. I haven't run it or written any tests. `check_config` now returns violated ids in order, AL-1 to AL-5, and nothing else.

- **AL-3:** it fails unless `retention_days` is an integer of at least 365. A missing value, a non-integer or a boolean all fail.
- **AL-4:** it fails unless `fields` is a list, tuple or set containing `user`, `action`, `timestamp` and `outcome`. A missing `fields` also fails.
- **AL-5:** it fails unless `tamper_protection` is `True`.

I left the existing AL-1 and AL-2 checks as they were. AL-2 still treats a missing `destination` as `"stdout"`, so it counts as a violation.
