`validate_upload` now enforces the three rules, and the checks pass: pytest (21 tests), ruff check, ruff format, and ty. The ty run needed `--extra-search-path src`, because ty can't resolve `uploads` on its own. That error was there before my change, and I left the project config alone.

- **Extension:** it must be `.pdf`, `.png` or `.csv` in any case. Otherwise it raises `UploadRejected("file extension is not allowed")`.
- **Path separator:** a `/` or `\` anywhere in the filename is rejected, not stripped. The message is `"filename must not contain a path separator"`.
- **Leading dot:** a filename starting with `.` is rejected with `"filename must start with a dot"`. This also catches `..`.
- **Stored name:** the function returns the filename lowercased.
- **Size:** the size check and its message are unchanged, and it still runs first.

I also fixed a bug in `extension_of` in `src/uploads/naming.py`. For a name with no dot it returned the whole name, so a file literally called `pdf` would have passed as a PDF. It now returns an empty string when there's no dot.

`base_name` in `naming.py` is no longer used by validation. I left it in place.

I added tests in `tests/test_validation.py` for each rule, including the case variants, `pdf`, `a.`, `a.pdf.exe`, and both separator styles.

`uv run ty check` with no arguments also reports 14 errors in the parent repo's `scripts/` directory. Those are unrelated to this work.
