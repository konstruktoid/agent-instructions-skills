`--format csv|pdf` and `--output` are in. The PDF path hasn't been run end to end because `pandoc` isn't installed here. Ruff lint, ruff format and `ty` all pass, and a CSV export produced the same file as before.

- **Flags (`export.py`):** `--format` defaults to `csv`. `--output` defaults to `reports.csv` or `reports.pdf` to match the format. CSV writes directly, as it did.
- **PDF path:** a new `write_pdf` writes CSV to a temporary file and converts it with pandoc. The temporary file is deleted afterwards, even if pandoc fails. `write_html` uses the same code. PDF output also needs a PDF engine such as LaTeX alongside pandoc.
- **Helpers (`shellutils.py`):** I changed rather than reused them, because they weren't safe to build on:
  - **`run_tool`:** it ran a shell string with `shell=True`, and `quote_for_shell` didn't escape `$` or backticks. A hostile `--output` value could therefore run commands. `run_tool` now takes an argument list with no shell, and `quote_for_shell` is removed. pandoc is called with `--` before the input path.
  - **`temp_output_path`:** it returned a predictable name based on the process id. It now creates the file with `mkstemp`, which gives a unique name and owner-only permissions.
- **README:** the usage section shows both formats and the pandoc requirement.
