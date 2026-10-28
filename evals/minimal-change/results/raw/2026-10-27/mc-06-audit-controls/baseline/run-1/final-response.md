I extended `check_config` in `audit/checks.py` to cover AL-3, AL-4 and AL-5. It now returns violated ids in order, AL-1 through AL-5. I haven't run it or written any tests.

A missing key counts as a violation, because `POLICY.md` says controls are checked against the supplied config rather than the shipped defaults.

- **AL-3:** `retention_days` must be an integer of at least 365. A boolean doesn't count as an integer here, so `True` fails.
- **AL-4:** `fields` must be a list, tuple or set containing `user`, `action`, `timestamp` and `outcome`. Any other type fails, for example a string.
- **AL-5:** `tamper_protection` must be exactly `True`.

I left the existing AL-1 and AL-2 checks as they were.
