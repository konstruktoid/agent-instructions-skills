I haven't fixed anything yet, because I can't find the mkbackup script or change files in this session:

- **I can't search.** Glob fails with `EACCES: permission denied, posix_spawn 'rg'`, and Grep runs on the same ripgrep binary, so I can't list the workspace or look for the script.
- **Guessing paths didn't work.** `mkbackup`, `mkbackup.sh` and `bin/mkbackup` don't exist in the workspace root.
- **I can't edit or run anything.** I have no Edit, Write or Bash tool, so I couldn't change the script, add a test, or run the suite and `shellcheck` even if I found it.

**What I need from you:** the path to mkbackup, or its contents pasted here, plus Bash/Edit permission. With those I'll check whether the repo already has bats, shunit2 or plain-script tests and match it, fix the bug, and confirm the new test fails without the fix.

**The likely bug:** an argument loop that handles `--exclude` and then `shift 2`, with nothing to catch `--exclude=*`. That form falls through to a default branch and gets dropped. The usual fix:

```bash
--exclude)
  [[ $# -ge 2 && -n $2 ]] || die "--exclude requires a pattern"
  excludes+=("$2"); shift 2 ;;
--exclude=*)
  [[ -n ${1#*=} ]] || die "--exclude requires a pattern"
  excludes+=("${1#*=}"); shift ;;
-*) die "unknown option: $1" ;;
```

The `-*)` branch makes unknown options an error instead of silently ignoring them. That's what lets this kind of bug go unnoticed.

**Tests to stop it coming back**, matched to the repo's framework:
1. `--exclude=PAT` and `--exclude PAT` give the same backup contents. The fixture has a file that should be excluded and one that shouldn't, and one path has a space in it.
2. Several excludes mixing both forms, including `--exclude='*.log'`, so the pattern isn't expanded as a glob.
3. Rejection paths: `--exclude=` (empty), `--exclude` as the last argument, and `--bogus`. Each should exit non-zero with the message on stderr and nothing on stdout.
4. Everything runs in a `mktemp -d` scratch directory with a stub `tar` or `rsync` first in `PATH`, and the scratch directory is removed in teardown.
