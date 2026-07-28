All done. Summary of changes:

- **`src/reportkit/export.py`**: `main()` now has `--format {csv,pdf}` (default `csv`) and `--output` (defaults to `reports.csv`/`reports.pdf` based on format). Added `write_pdf`, mirroring `write_html`'s pattern — CSV to a temp file, then `convert()` through pandoc. `convert()` now calls `run_tool` with an argv list instead of a shell string.
- **`src/reportkit/shellutils.py`**: `run_tool` takes a `list[str]` and runs `subprocess.run` without `shell=True`, so paths (which can contain spaces or shell metacharacters) never need quoting and can't be interpreted as shell syntax — this removed the need for `quote_for_shell`, which I deleted. `temp_output_path` now uses `tempfile.mkstemp` instead of a pid-based guessed name, so the intermediate file is created atomically and privately rather than being predictable/race-able.
- **`README.md`**: documents both `--format` values and the output defaults.

Verified: `ruff check .` and `ty check .` both pass; CSV export produces correct output; PDF export correctly writes the intermediate CSV and invokes `pandoc` with the destination path as a distinct argv element (confirmed with a path containing a space) — it only fails because pandoc isn't installed in this sandbox, which is expected and outside the scope of this change.
