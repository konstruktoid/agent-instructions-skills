`--format csv|pdf` and `--output` are in. I couldn't test the PDF path because pandoc isn't installed here. `ruff check`, `ruff format --check` and `ty check` all pass, and a CSV export to a path containing a space and `$` wrote the expected file.

- **CLI** (`src/reportkit/export.py`): `--format` accepts `csv` (the default) or `pdf`. `--output` defaults to `reports.csv` or `reports.pdf` to match the format. CSV runs the same `write_csv` code as before, and plain `python -m reportkit.export` still writes `reports.csv`. A new `write_pdf` writes CSV to a temporary file, then converts it with pandoc.
- **Shell injection fix** (`src/reportkit/shellutils.py`): `run_tool` ran a shell string with `shell=True`, and `quote_for_shell` only wrapped values in double quotes. A `--output` value containing `$(...)` or a backtick would have run as a command. `run_tool` now takes an argument list with no shell, and I removed `quote_for_shell`.
- **Temp file fix** (`src/reportkit/shellutils.py`): `temp_output_path` used a predictable `/tmp/reportkit-<pid>` name that another local user could pre-create or symlink. It is now a context manager that gives a file path inside a private temporary directory, deleted on exit. `write_html` was updated to use both changes.
- **README**: the usage section documents both formats. It notes that PDF export needs pandoc and a PDF engine such as LaTeX on `PATH`.

I haven't committed anything.
