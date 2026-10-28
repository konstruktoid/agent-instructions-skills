I extended `check_config` in `audit/checks.py` to cover AL-3, AL-4 and AL-5, so it now checks all five controls in `POLICY.md`. I haven't run it or any tests.

- **AL-3:** a violation unless `retention_days` is an integer of at least 365. A boolean doesn't count as an integer, so `True` fails.
- **AL-4:** a violation unless `fields` includes `user`, `action`, `timestamp` and `outcome`.
- **AL-5:** a violation unless `tamper_protection` is `True`.

A missing key counts as a violation for each of these, as `POLICY.md` says a control the defaults would satisfy is still checked against the config supplied. The ids come back in order AL-1 to AL-5.
