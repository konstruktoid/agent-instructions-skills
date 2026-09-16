PDF path correctly writes CSV to a temp file and invokes `pandoc [...] -o /tmp/out.pdf` as an argument list, no shell involved. `pandoc` itself isn't installed in this sandbox, so I couldn't exercise a real conversion end-to-end — flagging that explicitly rather than claiming full verification.

Changed files:
- `src/reportkit/export.py` — added `--format {csv,pdf}` (default `csv`) and made `--output` default per-format; renamed `write_html` to `write_pdf`; `convert` now builds an argument list instead of a shell string.
- `src/reportkit/shellutils.py` — `run_tool` now takes a list and runs without `shell=True`; removed `quote_for_shell` (no longer needed, was the only caller).
- `README.md` — documented both formats and the `--format`/`--output` defaults.

`ruff check`, `ruff format --check`, and `ty check` all pass. Note: I dropped `shell=True` + manual quoting in favor of list-based `subprocess.run`, since `--output` is user-supplied and shouldn't be parsed by a shell — this deviates from "reuse the helpers as-is" but keeps within the "reuse or change as you judge best" latitude the task gave.
