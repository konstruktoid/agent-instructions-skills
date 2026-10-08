I couldn't write the test because `parse_flags` doesn't exist in this repository.

- A search for `parse_flags` found no matches in any file.
- The only shell file is `scripts/backup.sh`. It's a flat script with no functions, and it doesn't parse flags or arguments at all.
- There's no shell test setup (no bats, shunit2, `test_*.sh` or Makefile target). The only test is `tests/test_balance.py`, which is Python.

I didn't want to guess at what the function should do, so I haven't written anything.

- **Different branch or repo:** If the library lives elsewhere, tell me the path or branch. I'll read its existing tests and match their style.
- **Not written yet:** If you want me to write `parse_flags` first, I need its intended flags and behavior. I'd put it in a sourceable library file and test it with bats.
- **`backup.sh` is what you meant:** It has no flag parsing today. A regression test for it would need a stated behavior to lock in. It also has its own problems: unquoted variables, no error handling, and `rm -rf` on a `/tmp` path. I can cover those if you want.
