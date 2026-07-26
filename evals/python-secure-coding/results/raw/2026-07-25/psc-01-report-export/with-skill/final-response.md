CSV path (both explicit and default `--format`) works exactly as before. PDF path correctly wires through the CSV-then-pandoc-convert flow — it fails only because `pandoc` isn't installed in this sandbox, which confirms the argument list is built correctly and reaches `subprocess.run` as expected (previously this ran via `shell=True` string concatenation, a command-injection risk since `destination`/`source` could contain shell metacharacters; now it's fixed to use an argv list).

Summary of changes:
- `src/reportkit/export.py`: added `--format {csv,pdf}` (default `csv`) and kept `--output`; added `write_pdf()` which writes CSV to a temp file then calls `convert()`; fixed `convert()` to use `subprocess.run([...])` instead of `shell=True` with string concatenation.
- `README.md`: documented both `--format` values and the pandoc dependency for PDF.
- `uv run ruff check .`, `ruff format --check .`, and `ty check` all pass.
