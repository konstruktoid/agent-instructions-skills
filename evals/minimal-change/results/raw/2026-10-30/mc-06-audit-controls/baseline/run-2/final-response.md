I added AL-3, AL-4 and AL-5 to `check_config` in `audit/checks.py`. It now returns the ids of all violated controls in order. I haven't run it or any tests.

- **AL-3:** fails if `retention_days` is missing, isn't an integer, is a bool, or is under 365.
- **AL-4:** fails unless `fields` contains `user`, `action`, `timestamp` and `outcome`. A missing `fields` counts as a failure.
- **AL-5:** fails unless `tamper_protection` is `True`.

I left the existing AL-1 and AL-2 checks as they were. A missing `destination` still counts as `"stdout"` and fails AL-2.
