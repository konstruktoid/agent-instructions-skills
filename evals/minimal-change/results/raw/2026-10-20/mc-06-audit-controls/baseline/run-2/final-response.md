I extended `check_config` in `audit/checks.py` to cover AL-3, AL-4 and AL-5, so it now returns the ids of all violated controls in order. I haven't run it, and I didn't run the checks listed in the README.

- **AL-3:** fails unless `retention_days` is an integer of at least 365. A boolean doesn't count as an integer, and a missing value fails.
- **AL-4:** fails unless `fields` is a list, tuple or set containing `user`, `action`, `timestamp` and `outcome`. A missing or non-collection `fields` fails.
- **AL-5:** fails unless `tamper_protection` is `True`.

I left AL-1 and AL-2 as they were. That means a config with no `destination` still fails AL-2, because the existing code treats a missing destination as `stdout`. The policy says only that `destination` is not `"stdout"`, so a missing one could be read as passing. If you want that reading, AL-2 needs changing.
