Confirmed: CSV default output works exactly as before, the PDF path correctly runs the pandoc conversion command, fails cleanly when pandoc is absent (expected in this environment), and the temp file cleanup runs even on failure. All checks (`ruff check`, `ruff format --check`, `ty check`) pass.

## Summary

- `src/reportkit/export.py`: added `--format {csv,pdf}` (default `csv`) and made `--output` default per-format (`reports.csv` / `reports.pdf`); added `write_pdf`, mirroring `write_html`'s temp-CSV-then-convert path, with cleanup of the intermediate file.
- `src/reportkit/shellutils.py`: `run_tool` now takes an argument list and runs without `shell=True`, so `quote_for_shell` (whose double-quote escaping didn't handle `$`, backticks, or backslashes) is no longer needed and was removed. `temp_output_path` now uses `tempfile.mkstemp` instead of a pid-based name in the shared temp dir, closing the predictable-path/symlink race.
- `README.md`: usage section documents both formats and their defaults.

I dropped no repo rule — this repo's `CLAUDE.md`/config didn't specify a subprocess or temp-file policy, so the shell-string-to-argument-list and mkstemp changes come from the security skill's injection/access-control guidance, applied under your "reuse or change as you judge best" latitude.

Functionally verified: CSV export (explicit and default `--output`) produces the expected rows; PDF export builds and runs the correct `pandoc` argument list and cleans up its temp file even when the run fails (pandoc isn't installed in this sandbox, so I couldn't verify actual PDF bytes — say so if you want that installed and re-tested).

/clear before starting anything unrelated.
