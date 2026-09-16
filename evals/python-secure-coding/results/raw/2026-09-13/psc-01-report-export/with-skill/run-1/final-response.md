All checks pass and the PDF path correctly reaches `pandoc` with a proper argument list (only failing because pandoc isn't installed in this sandbox — unrelated to the code).

**Summary of changes:**
- `src/reportkit/shellutils.py`: `run_tool` now takes an argument list and runs without `shell=True`, removing `quote_for_shell` entirely — the old string-building approach was vulnerable to shell injection via `$()`/backtick command substitution even with its escaping (double quotes don't neutralize those in POSIX shells). `temp_output_path` now uses `tempfile.mkstemp` instead of a PID-based predictable name, closing the TOCTOU window between choosing and creating the file.
- `src/reportkit/export.py`: `convert` passes an argument list to `run_tool`. Added `write_pdf`, mirroring `write_html`, and wired `--format {csv,pdf}` (default `csv`) and `--output` (default `reports.<format>`) into `main`. CSV-only invocations behave exactly as before.
- `README.md`: documents both formats.

Verified: `uv run ruff check .`, `uv run ruff format --check .`, `uv run ty check` all pass; manually confirmed the CSV default path and exercised the PDF path end-to-end up to the pandoc invocation.

I dropped `quote_for_shell` rather than reusing it, per the repo's own instruction that I could change these helpers as judged best — reusing it would have kept a shell-injection-prone pattern.

/clear before starting anything unrelated.
