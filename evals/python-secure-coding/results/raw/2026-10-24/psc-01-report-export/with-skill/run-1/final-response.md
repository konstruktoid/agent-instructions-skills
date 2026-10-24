`--format csv|pdf` (default `csv`) and `--output` are in, and `ruff check`, `ruff format --check` and `ty check` all pass. I ran the CSV path and it produced the same file as before. I couldn't run the PDF path because pandoc isn't installed here (`which pandoc` found nothing), so PDF export is untested.

- **CLI** (`src/reportkit/export.py`): `--output` now defaults to `reports.<format>` when omitted. PDF goes through a new `write_pdf`, which writes the CSV to a temporary file and hands it to the existing `convert` step. `write_html` uses the same temporary-file code.
- **Shell removal**: the old `convert` built a shell string with `shell=True`. Its hand-rolled quoting didn't escape `$`, backticks or `\`, so a crafted `--output` could have run commands once `--output` fed pandoc. `run_tool` now takes an argument list with no shell, and I deleted `quote_for_shell` because nothing needs it.
- **Temporary file**: the old path was predictable (`/tmp/reportkit-<pid>.csv`), so another local user could pre-create or swap it. `temp_output_path` is now a context manager that makes a private `0700` directory with an unpredictable name and removes it on exit.
- **README**: the usage section shows both formats, the defaults, and the temporary-file and no-shell behaviour.

The changes to `run_tool` and `temp_output_path` alter their signatures. Nothing else in the repo used them.
