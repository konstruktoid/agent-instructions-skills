`check_config` in `audit/checks.py` now checks AL-3, AL-4 and AL-5 as well as AL-1 and AL-2, and returns the violated ids in order.

- **AL-3:** `retention_days` must be an integer of at least 365. A missing value, a non-integer or a boolean fails.
- **AL-4:** `fields` must contain `user`, `action`, `timestamp` and `outcome`. A missing or non-list value fails.
- **AL-5:** `tamper_protection` must be `True`.

I ran it two ways. An empty config returns all five ids. A fully compliant config returns an empty list. The one existing test in `tests/test_checks.py` passes. I ran it with `unittest` because pytest isn't installed. I didn't add new tests.

I left the AL-2 check as it was. A config with no `destination` is treated as `"stdout"` and fails AL-2.
