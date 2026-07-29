All good — the CSV path is byte-for-byte the same as before (both explicit `--output` and the new default-per-format behavior), and the PDF path correctly reaches pandoc with a clean argument list (it only fails here because pandoc isn't installed in this sandbox). Checks pass:

- `uv run ruff check .` — clean
- `uv run ruff format --check .` — clean
- `uv run ty check src` — clean (the unscoped `ty check` hits a pre-existing, unrelated failure from an outer repo's `scripts/check_skills.py`/`yaml` import — reproduced identically on the unmodified baseline via `git stash`, so it's environment noise, not something introduced here)

## Summary

- `--format {csv,pdf}` (default `csv`) and `--output` (defaults to `reports.csv`/`reports.pdf` per format) added to `reportkit.export`.
- `write_pdf()` writes CSV to a temp file, then reuses `convert()`/pandoc, mirroring the existing `write_html()` path.
- Hardened `shellutils.py` while touching it, since the task explicitly allowed changing the helpers: `run_tool` now takes an argument list and runs without `shell=True` (dropping the unsafe `quote_for_shell` string-quoting scheme, which didn't actually neutralize shell metacharacters like `$()`/backticks), and `temp_output_path` now uses `tempfile.mkstemp` instead of a PID-guessable path, closing a predictable-path/TOCTOU race.
- README usage section documents both formats and the temp-file conversion path.
