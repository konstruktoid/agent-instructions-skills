This confirms the wiring is correct — it reaches `convert()`, writes the CSV to a temp file, and calls pandoc as expected. It fails only because pandoc isn't installed in this sandbox, which is expected/environmental, not a code issue.

Summary of changes:
- `src/reportkit/export.py`: added `--format {csv,pdf}` (default `csv`); `write_pdf()` writes CSV to a temp directory then calls the existing `convert()` pandoc helper. Also fixed `convert()` to use `subprocess.run([...], check=True)` instead of `shell=True` with string-concatenated paths (a command-injection risk, since `--output` is user-controlled).
- `README.md`: documented both `--format` values and the PDF-via-temp-CSV flow.
- `ruff check` and `ty check` both pass.
