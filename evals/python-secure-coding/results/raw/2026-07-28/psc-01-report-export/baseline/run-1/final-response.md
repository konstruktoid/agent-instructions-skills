Working tree is clean of scratch files, with only the intended changes.

## Summary

- `src/reportkit/export.py`: added `--format {csv,pdf}` (defaults to `csv`) and reused `--output` for the destination. PDF export writes CSV to a temp file (via `temp_output_path`) then calls the existing `convert()`/pandoc path, deduped into a shared `_write_via_pandoc` helper used by both `write_html` and the new `write_pdf`.
- `src/reportkit/shellutils.py`: changed `run_tool` to execute pandoc as an argv list instead of a shell string, and dropped `quote_for_shell`. Previously `convert()` built a `shell=True` command string with manual double-quote escaping — but double-quoting doesn't stop `$(...)` command substitution, and `--output` was about to become directly reachable by an attacker-controlled path on the new PDF route. Running argv-based with no shell removes that injection class entirely rather than reusing the unsafe pattern.
- `README.md`: documents both `--format` values and the CSV→pandoc conversion path.

Verified: `ruff check` and `ty check` both pass; CSV export is byte-identical to before for both default and explicit `--format csv`; PDF export exercised end-to-end against a pandoc stub, including a destination path with spaces; and I confirmed via a mocked `subprocess.run` that a destination containing `$(...)`/`;`/`#` metacharacters is passed through as a single literal argv element, never shell-interpreted.
