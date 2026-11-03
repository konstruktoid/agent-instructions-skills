I haven't been able to make this fix. I couldn't find the script, and this session has no tools that could change it.

What went wrong:

- **Search is broken.** Glob fails with `EACCES: permission denied, posix_spawn 'rg'`, so file search can't run in this environment, and Grep uses the same tool.
- **The script isn't at any path I guessed.** I tried `mkbackup`, `mkbackup.sh`, `bin/mkbackup` and `scripts/mkbackup.sh` in the workspace.
- **I can't edit or run anything.** I can only read files: there's no Edit/Write or Bash tool here. So even with the script found, I couldn't change it, add a test, or run the test suite and `shellcheck`.

To get this done, either:

1. Re-run the session with Bash and Edit/Write enabled, and make sure `rg` can run. Then I'll find the script and the existing tests, fix the parser, add a test that fails without the fix, and run the suite through the repo's own test command.
2. Or give me the script's path and paste its argument-parsing section, and I'll write the patch and the test for you to apply.

The bug is most likely an option parser that only matches the separate `--exclude` word and drops the `--exclude=PATTERN` form. The fix would add a branch like:

```bash
--exclude=*) excludes+=("${1#--exclude=}") ;;
```

next to the existing `--exclude)` case. It would also reject an empty pattern in both forms. The test would check that both `--exclude=PAT` and `--exclude PAT` give the same exclude list, using a pattern that contains a space. It would also check that `--exclude=` with nothing after it exits non-zero and prints an error to stderr. I haven't seen the script, so I can't confirm the bug is what I've guessed.
