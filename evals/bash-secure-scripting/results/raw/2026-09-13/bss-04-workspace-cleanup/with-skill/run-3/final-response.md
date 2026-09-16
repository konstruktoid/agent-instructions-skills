`bin/clean-workspaces.sh` and `README.md` changed. Deviated from the skill's example skeleton where it was internally inconsistent (placeholder text like `local sig="bin/clean-workspaces.sh"` in the reference code — not usable as-is); I wrote the trap/argument-parsing logic from the skill's stated principles instead of copying that snippet.

Verification: `shellcheck` and `bash -n` both clean; `shfmt` isn't installed so the formatter step couldn't run. Ran against a disposable copy of the `workspaces/` fixture (including the `old build 2024` directory with a space in its name): `--help`, `--dry-run` (left the fixture untouched, listed the correct stale entry), a real run (removed only the stale directory, exit 0), and two failure paths (`--workspace-root` pointing at a nonexistent dir → exit 1, invalid `--days abc` → exit 64), both reporting to stderr.

No locking was added for concurrent invocations — not requested, and the original script didn't have it either.
