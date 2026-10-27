I extended `check_config` in `audit/checks.py` to cover AL-3, AL-4 and AL-5. It now returns violated control ids in order, AL-1 through AL-5. I didn't run it or any tests.

- **AL-3:** a violation unless `retention_days` is an integer of at least 365. A missing value, a non-integer, or a boolean (`True` would otherwise count as 1) all fail.
- **AL-4:** a violation unless `fields` is a list, tuple or set containing `user`, `action`, `timestamp` and `outcome`. A missing `fields` also fails.
- **AL-5:** a violation unless `tamper_protection` is `True`.

I left the existing AL-1 and AL-2 checks as they were. That means a config with no `destination` counts as stdout and fails AL-2.
