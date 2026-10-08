`--format csv|pdf` (default `csv`) and `--output` now work. I couldn't run a real PDF conversion because `pandoc` isn't installed here.

I ran `ruff check`, `ruff format --check` and `ty check`, and all three pass. The CSV path gave the same output as before, including an output path with a space in it. The PDF path ran as far as launching `pandoc`, then failed with "No such file or directory: 'pandoc'". Nothing beyond that launch was exercised, and real PDF output also needs a PDF engine such as LaTeX.

**Changes**
- **`src/reportkit/export.py`:** a new `write_pdf` writes the CSV to a temporary file and converts it with `pandoc`. The CLI chooses between `write_csv` and `write_pdf` from `--format`. `--output` defaults to `reports.<format>`.
- **`src/reportkit/shellutils.py`:** I changed the helpers rather than reusing them as they were.
  - **`run_tool`:** it now takes an argument list and runs without a shell. The old `quote_for_shell` only escaped `"`, so a `--output` value containing `$(...)`, backticks or `$VAR` would have run as a command. I removed `quote_for_shell` because nothing needs it now.
  - **`temp_output_path`:** it now yields a path inside a private temporary directory that is deleted on exit. The old process-id path in `/tmp` was predictable and was never cleaned up.
- **`write_html`:** it uses the same helpers, so it picked up both fixes.
- **`README.md`:** the usage section shows both formats and the `--output` default, and notes the `pandoc` requirement.

I didn't commit anything.
