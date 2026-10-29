I added checks for AL-3, AL-4 and AL-5 to `check_config` in `audit/checks.py`. It now covers all five controls and returns the failing ids in order. I haven't run it or written any tests.

- **AL-3:** a missing, non-integer or `bool` `retention_days`, or one below 365, fails. I excluded `True`/`False` explicitly, because Python treats them as integers.
- **AL-4:** it fails unless `fields` contains all of `user`, `action`, `timestamp` and `outcome`. A missing `fields` counts as a failure.
- **AL-5:** it fails unless `tamper_protection` is exactly `True`.

I left the existing AL-1 and AL-2 checks as they were.
