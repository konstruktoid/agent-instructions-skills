`--format csv|pdf` (default `csv`) and `--output` now work. The PDF path itself hasn't run, because `pandoc` isn't installed here, so I couldn't produce a real PDF.

Checks: `ruff check`, `ruff format --check` and `ty check` all pass. I also ran the CSV path from the command line, and it writes the same output as before. The repository has no test suite.

- **PDF export:** `write_pdf` writes the CSV into a temporary directory, then calls pandoc on it through the existing `convert` helper. `--format csv` still just writes the CSV.
- **Helper changes:**
  - **Shell injection:** `run_tool` used `shell=True`, and `quote_for_shell` didn't escape `$` or backticks, so a crafted `--output` path could run arbitrary commands. `run_tool` now takes an argument list and runs without a shell. I removed `quote_for_shell` because nothing needs it any more.
  - **Temp files:** `temp_output_path` returned a predictable path in `/tmp`, which a local user could pre-create or symlink. It is replaced by a `temp_workdir()` context manager that makes a private directory and cleans it up. `write_html` uses it too.
- **README:** the usage section documents both formats. It notes that pandoc picks the output type from the extension, so the PDF path should end in `.pdf`, and that PDF export needs pandoc plus a PDF engine such as LaTeX.
