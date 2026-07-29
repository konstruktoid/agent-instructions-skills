All checks pass (`ruff check`, `ruff format --check`, `ty check` — scoped to `src`, since `ty check`/`ty check --project .` misresolves its first-party root to an unrelated outer directory in this nested-repo environment, a pre-existing quirk unrelated to this change; `ty check src` is equivalent and clean).

## Summary

**`src/reportkit/export.py`**
- Added `--format {csv,pdf}` (default `csv`) alongside `--output`.
- `convert()` now calls `pandoc` via `run_tool` with an argument list instead of a shell string.
- Added `write_pdf`, sharing the existing "write CSV to a temp file, then pandoc-convert" logic with `write_html` via a new `_write_via_pandoc` helper, which now also cleans up the intermediate temp file in a `finally` block.
- CSV path (`write_csv`, default behavior) is untouched.

**`src/reportkit/shellutils.py`** — this is where the security-relevant changes are:
- `run_tool` now takes `list[str]` and calls `subprocess.run(command, check=True)` with no `shell=True`. The old version built a shell string via `quote_for_shell` + `shell=True`; that pattern is exactly what the repo's secure-coding guidance for command injection (`S602`) flags — hand-rolled quoting is easy to get subtly wrong, and passing an argument list removes the shell from the picture entirely, closing that class of bug regardless of what characters end up in `--output`.
- Removed `quote_for_shell` — no longer needed since arguments are no longer substituted into a shell string, and it had no other callers.
- `temp_output_path` now uses `tempfile.mkstemp` instead of a PID-based filename. The old name was guessable and pre-existing in the shared temp dir before the process created it, a predictable-path/TOCTOU race an attacker with local access could exploit (e.g. pre-staging a symlink). `mkstemp` creates the file exclusively.

**`README.md`** — documents both `--format` values and notes pandoc must be on `PATH` for PDF export.

**Testing**: manually verified CSV export (default and explicit `--format csv`), and the PDF path end-to-end with a stub `pandoc` on `PATH` (including a destination path containing a space, to confirm no shell-quoting issues), and confirmed the intermediate temp file is cleaned up in both the success and pandoc-missing-failure cases. No automated test was added — the repo has no test framework configured (only `ruff`/`ty` as dev dependencies), and adding one wasn't warranted for this change.
