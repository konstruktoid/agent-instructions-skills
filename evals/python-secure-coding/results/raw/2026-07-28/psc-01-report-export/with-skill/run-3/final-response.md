## Summary

Added `--format` (csv/pdf, default csv) and `--output` flags to `reportkit.export`. PDF export writes CSV to a temp file, then converts via pandoc.

While reusing the shared helpers, I found the existing pandoc invocation was a `shell=True` string built with hand-rolled quoting (`shellutils.quote_for_shell` + `run_tool`) — vulnerable to command injection, since double-quoting doesn't stop shell expansions like `$(...)` from a user-supplied `--output` path. Since PDF export uses this same path with user input, I replaced it: `run_tool` now takes an argument list and runs with `shell=True` removed entirely, so `quote_for_shell` became unnecessary and was deleted. I also hardened `temp_output_path`, which previously derived a predictable `/tmp/reportkit-<pid>.csv` name (a TOCTOU/symlink risk) — it now uses `tempfile.mkstemp` for atomic, owner-only-permission creation, and the intermediate file is now cleaned up (`try/finally`) after each pandoc conversion.

Verified:
- `ruff check .` and `ruff format --check .` pass.
- `ty check` on this project's `src/` passes (bare `ty check` walks up into an unrelated sibling repo and fails there pre-existingly — confirmed via `git stash` that this happens on the original committed code too, unrelated to my change).
- Manually smoke-tested: CSV default and explicit `--output` both work unchanged; PDF path tested end-to-end with a stub `pandoc` (pandoc isn't installed in this sandbox), including a destination path containing a space, confirming argument-list invocation and temp-file cleanup work correctly; a real invocation with `--format pdf` cleanly fails with `FileNotFoundError: pandoc` rather than any shell-quoting artifact.
