I added AL-3, AL-4 and AL-5 to `check_config` in `audit/checks.py`, after the existing AL-1 and AL-2 checks. It returns the violated ids in order. I haven't run it or any tests.

- **AL-3:** a missing, non-integer or boolean `retention_days`, or one below 365, fails.
- **AL-4:** `fields` fails unless it is a list, tuple or set that contains `user`, `action`, `timestamp` and `outcome`.
- **AL-5:** anything other than `tamper_protection` being `True` fails, including a missing key.

The policy says shipped defaults don't count, so a missing key is treated as a violation for every control.
