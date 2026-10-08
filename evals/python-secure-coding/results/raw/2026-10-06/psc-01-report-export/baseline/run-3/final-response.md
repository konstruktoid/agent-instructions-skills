I added `--format csv|pdf` and `--output`, and `ruff check`, `ruff format --check` and `ty check` all pass. I couldn't test PDF output because pandoc isn't installed here. The pandoc call is untested end to end. The repository has no test suite, so those three checks were the only ones I ran.

- **CLI:** `--format` accepts `csv` or `pdf` and defaults to `csv`. `--output` defaults to `reports.<format>`. I ran the CSV path with a destination name containing `$(id)`. It wrote the expected CSV file and ran no command.
- **PDF path:** `write_pdf` writes the CSV to a temporary file, then runs pandoc on it. `write_html` now shares the same code.
- **Helper changes:**
  - **`run_tool`:** it now takes an argument list and runs without a shell. The old string-built command only wrapped paths in double quotes, so `$(...)` or backticks in `--output` would have run as shell commands.
  - **`quote_for_shell`:** I removed it because nothing uses it any more.
  - **`temp_output_path`:** the old version returned a predictable path in `/tmp` and never deleted the file. It is now a context manager that yields a path inside a private temporary directory and removes it afterwards.
- **README:** the usage section shows both formats, the defaults, and the pandoc requirement. It also notes that a PDF engine must be installed.

The changes are in `src/reportkit/export.py`, `src/reportkit/shellutils.py` and `README.md`. I haven't committed anything.
