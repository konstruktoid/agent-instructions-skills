I added `--format` (`csv` or `pdf`, default `csv`) and `--output`, which defaults to `reports.<format>`. I couldn't test PDF output, because pandoc isn't installed here. `ruff check`, `ruff format --check` and `ty check` all pass. I ran the CSV path and it writes the same file as before.

- **Command building (`shellutils.py`):** The old helper built a shell command string, with `shell=True` and a hand-rolled quote function. That could be broken out of by an `--output` value containing `"` or `$(...)`. I removed `quote_for_shell`. `run_tool` now takes an argument list and runs it with no shell, so `--output` is always a plain argument to pandoc.
- **Temp file (`shellutils.py`):** `temp_output_path` returned a path named after the process id in the shared temp directory. Another local user could predict or pre-create that name. It's now a context manager that creates a private temporary directory (`tempfile.TemporaryDirectory`) and deletes it afterwards.
- **Export code (`export.py`):** `write_html` and the new `write_pdf` share one conversion function that writes the CSV to the temporary file and then runs pandoc. `convert` calls `pandoc <source> -o <destination>`.
- **README:** The usage section shows both formats and notes that PDF needs pandoc plus a PDF engine such as LaTeX.

I didn't add tests, because the repository has no test setup.
