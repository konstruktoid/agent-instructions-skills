`--format {csv,pdf}` (default `csv`) and `--output` are in. `ruff check`, `ruff format --check` and `ty check` all pass. I only ran the CSV path end to end, and its output is unchanged. The PDF path is untested because pandoc isn't installed here.

- **Defaults:** `--output` defaults to `reports.csv`, or `reports.pdf` when `--format pdf` is given.
- **PDF path:** it writes the CSV to a private temporary directory, which is removed afterwards. It then calls pandoc with `-f csv`. `write_html` shares the same conversion function as the new `write_pdf`.
- **Helpers changed:** I changed the helpers rather than reusing them as they were:
  - **Shell quoting:** `run_tool` now takes an argument list and runs without a shell. The old `quote_for_shell` with `shell=True` still let `$(...)` and backticks in an `--output` path run as commands. I removed `quote_for_shell` because nothing needs it now.
  - **Temp file:** the old `temp_output_path` returned a predictable file name in the shared temp directory, which other users could pre-create or symlink. I replaced it with `tempfile.TemporaryDirectory` and removed the helper.
- **README:** the usage section now documents both formats, the defaults, and that PDF needs pandoc and a PDF engine such as LaTeX.

The repo has no test suite, so "the repository's checks" here means the ruff and ty configuration in `pyproject.toml`.
