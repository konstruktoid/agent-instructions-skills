`validate_upload` now enforces the three new rules, and the repo checks pass: `uv run pytest` (21 tests), `ruff check`, `ruff format --check`, and `ty check`.

- **Extension:** only `.pdf`, `.png` and `.csv` are accepted, in any case. Anything else raises `UploadRejected("file extension is not allowed")`.
- **Path separators:** a name containing `/` or `\` anywhere is rejected with `"filename contains a path separator"`. The old `base_name` stripping is gone from this path, so nothing is repaired.
- **Leading dot:** a name starting with `.` is rejected with `"filename starts with a dot"`.
- **Stored name:** a valid upload returns the filename lowercased.
- **Order of checks:** size is checked first, then separators, then the leading dot, then the extension.

`extension_of` in `src/uploads/naming.py` returned the whole name when there was no dot, so a file named `pdf` would have passed as a PDF. It now returns `""` in that case.

I added parametrized tests to `tests/test_validation.py`. They cover each rule, the case variants, and the rejection messages. They also cover the edge cases `pdf`, `a.`, `a.pdfx`, `../a.pdf` and `..\a.pdf`.

Bare `uv run ty check` fails. It picks up the parent repository's `scripts/` (missing `yaml`, type errors) and can't find the `uploads` package under `src`. With `--extra-search-path src src tests` it is clean, and it was also clean before my changes.

I did not commit anything.
