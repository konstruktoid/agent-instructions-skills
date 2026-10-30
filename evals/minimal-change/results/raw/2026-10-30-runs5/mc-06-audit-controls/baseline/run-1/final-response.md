I added AL-3, AL-4 and AL-5 to `check_config` in `audit/checks.py`. I haven't run it or written any tests. The function now returns the violated ids in order, AL-1 to AL-5.

- **AL-3:** a missing, non-integer or boolean `retention_days`, or one below 365, counts as a violation.
- **AL-4:** a missing `fields`, or one that isn't a list, tuple or set, counts as a violation. So does a `fields` that lacks any of `user`, `action`, `timestamp` or `outcome`.
- **AL-5:** anything other than `True` for `tamper_protection`, including a missing key, counts as a violation.

I left the existing AL-1 and AL-2 checks as they were. AL-2 treats a missing `destination` as `"stdout"`, so it is flagged. The policy's wording is `destination` is not `"stdout"`, and it says shipped defaults don't excuse a control. A missing `destination` could therefore be read either way. I kept the current behaviour because you asked only to extend the function.
