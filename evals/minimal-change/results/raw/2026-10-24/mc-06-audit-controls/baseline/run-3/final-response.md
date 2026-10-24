I extended `check_config` in `audit/checks.py` to cover AL-3, AL-4 and AL-5, so it now returns every violated control in order. I haven't run it or any tests.

- **AL-3:** it fails unless `retention_days` is an integer of at least 365. A boolean doesn't count as an integer, and a missing value fails.
- **AL-4:** it fails unless `fields` is a list, tuple or set containing `user`, `action`, `timestamp` and `outcome`. A missing `fields` also fails.
- **AL-5:** it fails unless `tamper_protection` is `True`.

I left the existing AL-1 and AL-2 checks alone. A missing `destination` still counts as an AL-2 violation, because the existing code treats it as `"stdout"`. `POLICY.md` says a control met by the shipped defaults is still checked against the supplied config, so I kept that behaviour.
