I extended `check_config` in `audit/checks.py` to check AL-3, AL-4 and AL-5 as well as the existing AL-1 and AL-2. It returns the failing ids in order. The one existing test passes. I didn't add tests for the new checks or run them against sample configs.

- **AL-3:** fails unless `retention_days` is an integer of at least 365. A missing value fails, and `True` or `False` don't count as integers.
- **AL-4:** fails unless `fields` is a list, tuple or set containing `user`, `action`, `timestamp` and `outcome`. A missing or malformed `fields` fails.
- **AL-5:** fails unless `tamper_protection` is `True`.

As with the existing AL-1 and AL-2 checks, a key missing from the supplied config counts as a violation. I didn't fall back to `audit/defaults.py`, since the policy says defaults still get checked against the supplied config.

`pytest` isn't installed here, so I ran the tests with `python3 -m unittest`.
