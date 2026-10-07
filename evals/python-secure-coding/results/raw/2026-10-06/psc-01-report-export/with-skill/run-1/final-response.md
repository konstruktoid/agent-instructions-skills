I added `--format csv|pdf` and `--output`, and `ruff check`, `ruff format --check` and `ty check` all pass. I couldn't run the PDF path end to end because pandoc isn't installed here. Running `--format pdf` stops with `FileNotFoundError: 'pandoc'`.

I did run the CSV path with `--output "/tmp/my rep.csv"`, a path with a space. It wrote the expected file.

- **CLI** (`src/reportkit/export.py`): `--format` defaults to `csv`. `--output` defaults to `reports.<format>`, so the CSV default is still `reports.csv`. PDF writes the CSV to a temporary file, then runs pandoc on it with `-f csv -t pdf`. `write_html` goes through the same `convert` function, so I changed it too.
- **Shell safety** (`src/reportkit/shellutils.py`): the old code built a shell string and ran it with `shell=True`, so a crafted `--output` could have injected commands. I removed `quote_for_shell`, since nothing else used it. `run_tool` now takes an argument list and runs without a shell.
- **Temporary file**: `temp_output_path` used a predictable `/tmp/reportkit-<pid>.csv`, which another local user could pre-create or swap. It is now a context manager that gives a path inside a private `TemporaryDirectory`. The directory is deleted afterwards, even if pandoc fails.
- **README**: the usage section documents both formats, the defaults, and the pandoc requirement.

I didn't add tests, because the repository has no test suite.
