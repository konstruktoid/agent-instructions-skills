I added `--format` (`csv` or `pdf`, default `csv`) and `--output`. I couldn't run the PDF path because `pandoc` isn't installed here. The checks pass: `ruff check`, `ruff format --check` and `ty check` are all clean.

The CSV path still writes the same file. I ran it with `--output "/tmp/a b.csv"` and got the expected rows. `--output` now defaults to `reports.<format>`, so the default CSV filename is unchanged.

PDF export writes the CSV to a temporary file and converts it with `pandoc --from csv`. That also needs a PDF engine, such as LaTeX, on the machine. I documented this in the README usage section, which now covers both formats.

I changed the shared helpers rather than reusing them as they were, because they weren't safe once `--output` could reach `pandoc`:
- **Shell command:** `run_tool` ran a shell string, and `quote_for_shell` only wrapped values in double quotes. A path containing `$(...)` or backticks would still have been executed. `run_tool` now takes an argument list and never uses a shell, and I removed `quote_for_shell`.
- **Temporary file:** `temp_output_path` returned a predictable path in `/tmp` based on the process id, which another user could pre-create or symlink. It's now a context manager that gives a file inside a private, randomly named temporary directory, deleted afterwards.
- **`# noqa: S603`:** the one suppression I added is on the `subprocess.run` call, with a justification next to it.
- **HTML export:** `write_html` still exists with the same behaviour.

`src/reportkit/__pycache__/` is untracked and not ignored, and I left it alone. I haven't committed anything.
