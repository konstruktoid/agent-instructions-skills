I added `--format csv|pdf` (default `csv`) and `--output`, and `ruff check`, `ruff format --check` and `ty check` all pass. I couldn't test the PDF path itself because pandoc isn't installed here. I did run the CSV export, and its output is unchanged.

- **`--output` default:** it now defaults to `reports.<format>`, so the CSV default is still `reports.csv`.
- **PDF path:** `write_pdf` writes the CSV to a temporary file and converts it through the existing `convert` function, which now runs `pandoc -f csv <src> -o <dest>`.
- **Shell removal:** `run_tool` now takes an argument list and no longer uses `shell=True`. The old `quote_for_shell` only escaped double quotes, so a value like `--output '$(cmd).pdf'` would have been run by the shell. With a list, paths go to pandoc as-is, and I removed `quote_for_shell`.
- **Temporary file:** `temp_output_path` used a predictable name in `/tmp`, based on the process id. It is now a context manager that creates a private directory (mode 0700) and deletes it afterwards. `write_html` uses it too.
- **README:** the usage section shows both formats and notes that PDF needs pandoc plus a PDF engine such as LaTeX.
