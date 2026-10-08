I couldn't find a `parse_flags` function in this repo, so I haven't written a test for it.

- A search for `parse_flags` returned no matches.
- The only shell file is `scripts/backup.sh`. It has no functions and no flag parsing: it's a straight-line backup script with hardcoded paths.
- The only existing test is `tests/test_balance.py`, a Python test. There are no `.bats` or shunit2 files, and no `Makefile` or `justfile`. The only workflow is `.github/workflows/deploy.yml`.

A test written now would be for code I'd have to invent, so I stopped here. Which of these is the case?

1. **The library is elsewhere.** It may be in another repo, a submodule, or a branch that isn't checked out. If so, give me the path.
2. **You want `parse_flags` added to `backup.sh`.** I'd need to know which flags it should accept, for example `--dry-run` or `--target`. Then I'd write the function and a test for it.
3. **The name is different.** If the function goes by another name, tell me which.

Once the code is in place, I'd use bats-core for the test. The repo has no shell test framework yet, so that would be new here. The test would source the library and call `parse_flags` directly. It would cover the exit codes, the rejection paths (unknown flag, missing value, a value starting with `-`), and a value containing a space. I'd also confirm it fails against a deliberately broken version.
