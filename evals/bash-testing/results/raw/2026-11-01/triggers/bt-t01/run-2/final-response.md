I haven't fixed anything yet: I can't find the mkbackup script, and this session can't edit files or run commands.

- **Finding the script:** File search fails with `EACCES: permission denied, posix_spawn 'rg'`, so I can't list the workspace. I tried the likely paths and none exist: `mkbackup`, `mkbackup.sh`, `bin/mkbackup`, `bin/mkbackup.sh` and `scripts/mkbackup.sh`.
- **Making changes:** I only have tools to read files and search for names and text. There's no edit, write or shell tool, so I couldn't apply a fix, add a test, or run the test suite and `shellcheck` even once I found the script.

**What I'd do once I have access:**
1. Look at the argument parsing. Usually the `case` statement only matches a separate `--exclude` and then reads the pattern from the next argument with `shift`. In that case `--exclude=PATTERN` either falls into a catch-all branch or gets silently ignored. The fix is to add a branch for `--exclude=*)` that takes the pattern from `"${1#--exclude=}"`. If the parser uses `getopts` or `getopt`, the fix is different, but the goal is the same.
2. Look for the repo's existing shell tests (bats, shunit2 or plain scripts) and add a test in the same style:
   - Run against a scratch directory whose path contains a space.
   - Check that `--exclude=PATTERN` and `--exclude PATTERN` produce the same backup contents.
   - Check that the excluded file is actually missing from the output, and check the exit status, not just the output.
   - Check that `--exclude=` with an empty pattern and a bare `--exclude` with nothing after it are both rejected with a message on stderr and a non-zero exit.
3. Run the test against the current code to confirm it fails, then apply the fix and run the full suite plus `shellcheck` and `bash -n`.

**What I need from you:**
- The path to the script and its test directory, or just paste the script's argument-parsing section.
- A session with edit and shell tools (or the permission that allows `rg` to run) so I can make the change and run the tests. Otherwise I can write out the exact diff and test file for you to apply.
