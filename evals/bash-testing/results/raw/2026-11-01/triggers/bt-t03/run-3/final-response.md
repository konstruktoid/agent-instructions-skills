I couldn't add the tests, because this workspace doesn't have an input validation script.

**What's in the workspace:**
- `scripts/backup.sh` is the only shell script. It's a nightly backup with hard-coded paths: it takes no arguments, reads no input and checks nothing, so there are no rejection paths to test.
- I searched every file for "valid", "empty", "too long" and "length". The only match was a line in `README.md:11` about a probe stalling on an empty directory, which has nothing to do with validating input.
- There are no shell tests and no test framework set up for shell scripts. The only test is `tests/test_balance.py`, a Python test for `src/ledger/balance.py`.

**Also:** in this session I can only read and search files. I have no tool to create or edit them or to run commands. So even with the right script, I couldn't write the tests or run them.

**To go ahead, I'd need:**
1. The script's location, if it's in another repository or branch, or confirmation that it should be written first. In that case I'd also need its rules: maximum length, allowed characters, and the exit code and message for each rejection.
2. A session where I can write files and run commands.

Once I have those, I'd test with whatever framework the repo already uses for shell tests, or say so if I add one. I'd cover these rejection cases: no arguments, too many, an empty string, a value one character over the limit (and one exactly at it), a value that fails the allowed-character check, and a value starting with `-`. Each test would check the exit code, that the error goes to stderr and that stdout stays empty. I'd also run `shellcheck` and `bash -n` on the test files.
