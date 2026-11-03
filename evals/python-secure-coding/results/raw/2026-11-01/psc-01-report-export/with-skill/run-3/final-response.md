I added `--format csv|pdf` (default `csv`) and `--output` to `reportkit.export`. I couldn't run the PDF path here because pandoc isn't installed. `ruff check`, `ruff format --check` and `ty check` all pass.

- **CSV path:** unchanged. I ran it with an output name containing `$(id)` and the file was written as expected, with the same contents as before.
- **PDF path:** `write_pdf` writes a temporary CSV and calls `pandoc --from=csv --output <dest> -- <csv>`. Pandoc picks the output format from the destination's extension, so `--output` for a PDF should end in `.pdf`, and pandoc needs a PDF engine such as pdflatex. If `--output` is omitted, the default is `reports.<format>`.
- **README:** the usage section now shows both formats and describes the flags.

I also changed the existing helpers rather than reusing them as they were:
- **Shell quoting:** `quote_for_shell` plus `shell=True` is injectable through `--output`, because `$(...)` and backticks still expand inside double quotes. `run_tool` now takes an argument list and runs without a shell, and I removed `quote_for_shell`.
- **Temporary path:** `temp_output_path` returned a predictable `/tmp/reportkit-<pid>.csv`, which another local user could pre-create or symlink. It is now a context manager that yields a path inside a private temporary directory, deleted on exit.
- **HTML:** `write_html` still works and now shares the same conversion function. It still can't be reached from the command line.

I added no tests, since the repo has none. There is a stray `src/reportkit/__pycache__/` from my smoke test, and I haven't committed anything.
