`--format csv|pdf` (default `csv`) and `--output` are added, and PDF goes through the existing pandoc path. I couldn't produce a real PDF here because `pandoc` isn't installed.

`ruff check`, `ruff format --check` and `ty check` all pass. The CSV run wrote the same output as before. For PDF, I put a stub `pandoc` on the path and ran with an output name containing `$(x)`. The stub received the right arguments, and the `$(x)` was not expanded. The stub was removed afterwards. The repository has no tests, so nothing else ran.

**Helper changes:** I changed the shared helpers rather than reusing them as they were, because `--output` is user input and two of them were unsafe for it.
- **`run_tool`:** it now takes an argument list and runs without a shell. The old string-and-`shell=True` version let `$(...)` or backticks in a path run commands, even after `quote_for_shell`. I removed `quote_for_shell` since nothing needs it now.
- **`temp_output_path`:** it is now a context manager that gives a path inside a private temporary directory, which is deleted afterwards. The old version returned a predictable file in `/tmp`, which another local user could pre-create or replace with a symlink.
- **`convert`:** it passes `--from csv` and a `--` separator so pandoc doesn't treat the file as an option.

**Other changes:**
- **Default output path:** if you leave out `--output`, it is `reports.csv` or `reports.pdf` to match the format. The old default was always `reports.csv`.
- **`write_html`:** it still works and shares the same conversion code as the new `write_pdf`.
- **README:** the usage section shows both formats and notes that PDF needs `pandoc` and a PDF engine such as LaTeX.

I didn't commit anything.
