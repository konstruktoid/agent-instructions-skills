pandoc isn't installed here, so I confirmed the PDF path invokes `run_tool(["pandoc", ...])` correctly up to the subprocess call, but couldn't exercise an actual conversion.

**Changes:**
- `src/reportkit/shellutils.py` — `run_tool` now takes argv (a list) and runs without `shell=True`; dropped `quote_for_shell`. The old code built a shell string with manual double-quote escaping around `--output`, which is a real command-injection hole (double quotes don't stop `$()`/backtick expansion in bash), so I fixed it rather than extend it to a new PDF path.
- `src/reportkit/export.py` — `convert` now passes argv directly to `run_tool`; added `write_via_csv` (shared by `write_html` and the new `write_pdf`) and `--format {csv,pdf}` (default `csv`) to `main`.
- `README.md` — documented both `--format` values and the PDF conversion path.

`ruff check` and `ty check` both pass. Default CSV export verified end-to-end; invalid `--format` values are rejected by argparse as expected.

Files changed: `src/reportkit/shellutils.py`, `src/reportkit/export.py`, `README.md`.
