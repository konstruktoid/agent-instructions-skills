PDF export is added, and the checks pass. I didn't run a real PDF export because `pandoc` isn't installed here.

`uv run ruff check .`, `uv run ruff format --check .` and `uv run ty check` are all clean. I confirmed that `write_csv` still produces the same CSV, and I did not run `main()` or the CLI flags.

**CLI (`export.py`)**
- `--format` takes `csv` or `pdf` and defaults to `csv`.
- `--output` sets the destination path. If it's omitted, the default is `reports.csv` or `reports.pdf` to match the format.
- The CSV path writes the file directly, as before.
- The PDF path writes CSV into a private temporary directory, runs pandoc on it, and deletes the directory afterwards.
- `write_html` now goes through the same helper as PDF.

**Changes to the shared helpers (`shellutils.py`)**
- **`run_tool`:** it now takes an argument list and no longer uses a shell. The old version ran a command string with `shell=True`, and its quoting only wrapped values in double quotes. A `--output` value containing `$(...)` or backticks would have been executed by the shell. I removed `quote_for_shell` because nothing needs it now.
- **`temp_output_path`:** I replaced it with a `temp_workdir()` context manager. The old version returned a predictable path (`/tmp/reportkit-<pid>.csv`) that another local user could pre-create or swap. `temp_workdir()` makes a private directory with an unpredictable name and cleans it up.
- **pandoc call:** the arguments are `--from csv --output <dest> -- <source>`.

**README:** the usage section now shows both formats and the defaults. It notes that PDF needs `pandoc` and a PDF engine such as LaTeX on `PATH`.

I haven't committed anything.
