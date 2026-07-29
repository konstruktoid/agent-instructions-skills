Done. Summary:

- `--format {csv,pdf}` (default `csv`) and `--output` flags added to `reportkit.export`; CSV behavior is unchanged and remains the default.
- `write_pdf` writes reports to a temp CSV then converts via the existing `convert()`/pandoc path, mirroring `write_html`.
- While wiring `--output` into the pandoc path, I found `run_tool` used `subprocess.run(shell=True)` with a hand-rolled quoting helper (`quote_for_shell`) that doesn't stop shell expansion of `$(...)`/backticks inside double quotes — a command-injection hole that a user-controlled `--output` path would have hit directly. Fixed by switching `run_tool` to take an argv list and dropping `shell=True` entirely; removed the now-unused `quote_for_shell`. Verified with a mocked subprocess that a malicious-looking output path (`weird $(touch /tmp/PWNED).pdf`) is passed through as a literal argv element with no injection.
- README usage section updated to document both formats and the default output paths.
- `ruff check` and `ty check` both pass; manually verified the CSV path still produces identical output and the PDF path builds the correct pandoc argv (pandoc itself isn't installed in this environment, so actual PDF generation wasn't exercised, only the code path up to the subprocess call).
