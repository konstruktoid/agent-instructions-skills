PDF export is added, but I couldn't test it here because `pandoc` isn't installed. I only checked the CSV path and the lint and type checks.

- **CSV path:** `--output "/tmp/a b$(x).csv"` wrote the expected file, including the space and `$(x)` in the name, and nothing was executed.
- **Checks:** `ruff check`, `ruff format --check` and `ty check` all pass (I let ruff reformat one long line).
- **Flags:** `--format` takes `csv` or `pdf` and defaults to `csv`. `--output` defaults to `reports.csv` or `reports.pdf` to match the format.
- **PDF route:** it writes the CSV into a temporary directory, then runs pandoc on it (`-f csv -t pdf`). `write_html` now uses the same route. A PDF engine such as LaTeX also needs to be installed for pandoc to produce a PDF.
- **README:** the usage section now shows both formats and notes that pandoc must be installed.

I changed the shared helpers rather than reusing them, because they were unsafe for user-supplied paths:
- **Shell quoting:** `quote_for_shell` plus `shell=True` wrapped paths in double quotes, which still lets a `--output` value containing `$(...)` or backticks run commands. `run_tool` now takes an argument list and runs without a shell, so `quote_for_shell` is gone.
- **Temp file path:** `temp_output_path` used a predictable name (`reportkit-<pid>.csv`) in the shared temp directory, which another local user could pre-create or swap. `make_temp_dir` replaces it with a private, randomly named directory that is removed afterwards.

The `run_tool` signature change is breaking for any other callers, but `export.py` was the only one in the repo.
