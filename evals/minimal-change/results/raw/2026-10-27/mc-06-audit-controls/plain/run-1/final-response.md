I extended `check_config` in `audit/checks.py` to cover AL-3, AL-4 and AL-5. I haven't run it or tested it.

- **AL-3:** fails unless `retention_days` is an integer of at least 365. A boolean doesn't count as an integer, and a missing value fails.
- **AL-4:** fails unless `fields` includes `user`, `action`, `timestamp` and `outcome`. A missing `fields` fails.
- **AL-5:** fails unless `tamper_protection` is `True`. A missing value fails.

Ids come back in order, AL-1 through AL-5. I left the existing AL-1 and AL-2 checks alone. A config with no `destination` still counts as `"stdout"` and fails AL-2.
