`--format {csv,pdf}` (default `csv`) and `--output` now work. I couldn't run a real PDF export because pandoc isn't installed here. `ruff check`, `ruff format --check` and `ty check` all pass, and a CSV export gives the same output as before. The change touches `src/reportkit/export.py`, `src/reportkit/shellutils.py` and `README.md`.

- **PDF path:** `--format pdf` goes through a new `write_pdf`, which writes CSV to a temporary file and converts it with pandoc. `--output` defaults to `reports.csv` or `reports.pdf` to match the format.
- **No more shell:** the old helpers built a shell string and ran it with `shell=True`, using a `quote_for_shell` function that didn't escape `$`, backticks or `\`. Now that `--output` is user-supplied, a crafted path could have run commands. `run_tool` now takes an argument list and runs it without a shell, and I removed `quote_for_shell`.
- **Temp files:** `temp_output_path` used a predictable `/tmp/reportkit-<pid>.csv`, which another local user could pre-create or symlink. It's now a context manager that gives a path inside a private temporary directory, deleted afterwards. `write_html` uses it too.
- **Output path:** `convert` passes the output as an absolute path, so a name starting with `-` can't be read as a pandoc option.
- **README:** the usage section shows both formats, the default, and that pandoc plus a PDF engine are needed for PDF.

`quote_for_shell` and the old `temp_output_path` signature are gone, so anything outside this repo that imported them will break. Nothing inside the repo uses them any more.
