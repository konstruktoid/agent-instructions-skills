I extended `check_config` in `audit/checks.py` to check AL-3, AL-4 and AL-5 as well as the existing AL-1 and AL-2. It returns the violated ids in order.

I ran it on two configs. An empty `{}` returns `['AL-1', 'AL-2', 'AL-3', 'AL-4', 'AL-5']`. A fully compliant config returns `[]`. I did not run `tests/test_checks.py`.

- **AL-3:** `retention_days` must be an integer of at least 365. A bool such as `True` does not count as an integer.
- **AL-4:** `fields` must be a list, tuple or set containing `user`, `action`, `timestamp` and `outcome`.
- **AL-5:** `tamper_protection` must be `True`.

A missing key counts as a violation. I did not fill in values from `audit/defaults.py`, because `POLICY.md` says controls are checked against the configuration supplied.
