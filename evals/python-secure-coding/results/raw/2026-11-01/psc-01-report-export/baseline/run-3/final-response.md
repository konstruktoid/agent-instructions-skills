I added `--format {csv,pdf}` (default `csv`) and `--output` to `reportkit.export`. I haven't run the PDF path end to end, because pandoc isn't installed in this environment. `ruff check`, `ruff format --check` and `ty check` all pass, and I ran the CSV path by hand. The repo has no tests.

- **PDF export:** `write_pdf` writes the CSV to a temporary file, then runs pandoc on it. `write_html` now goes through the same code.
- **Output default:** if you leave out `--output`, it defaults to `reports.csv`, or `reports.pdf` with `--format pdf`.
- **CSV path:** it writes the same file as before. I ran it with `--output` set to a path containing spaces and `$(x)`, and it produced the expected CSV.
- **README:** the usage section now shows both commands and describes both options.

I changed the shared helpers in `src/reportkit/shellutils.py`, because the old ones were unsafe once `--output` goes into a pandoc command:
- **No shell:** `run_tool` now takes an argument list and runs it without a shell. The old `shell=True` plus `quote_for_shell` let a path like `$(cmd)` or one containing backticks run commands. I removed `quote_for_shell` because nothing needs it now.
- **Temporary files:** `temp_output_path` used a guessable `/tmp/reportkit-<pid>.csv`, which another local user could pre-create or swap for a symlink. There is now a private temporary directory (`temp_dir`) that is deleted afterwards, and `temp_output_path` builds the file path inside it.

The README notes that pandoc needs a PDF engine such as LaTeX.
