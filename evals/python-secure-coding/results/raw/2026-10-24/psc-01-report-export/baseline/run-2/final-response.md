`--format csv|pdf` and `--output` are in. The CSV path works as before, but I haven't run a PDF export. `ruff check`, `ruff format --check` and `ty check` all pass. There are no tests in the repo. I also ran a CSV export to a path containing a space and a `$`, and it wrote the file correctly. `which pandoc` printed nothing because the earlier command failed before reaching it, so I don't know whether pandoc is installed here.

- **`export.py`**:
  - `--format` defaults to `csv`.
  - `--output` defaults to `reports.<format>`, so the CSV default is still `reports.csv`.
  - PDF goes through a new `write_pdf`. It shares a helper with `write_html`. The helper writes a temporary CSV, runs pandoc, and always deletes the temporary file.
- **`shellutils.py`**: I changed two helpers rather than reuse them as they were.
  - `run_tool` now takes an argument list and runs without a shell. The old shell-string version with `quote_for_shell` only escaped `"`. A `--output` containing `$(...)` or a backtick could have run commands, so I removed `quote_for_shell`.
  - `temp_output_path` now uses `tempfile.mkstemp`, which gives an unpredictable name and a private file. The old path was `reportkit-<pid>.csv` in the temp directory, which another local user could pre-create or symlink.
- **`README.md`**: the usage section shows both formats, the defaults, and how the PDF path works.

PDF output needs pandoc and a PDF engine on `PATH`.
