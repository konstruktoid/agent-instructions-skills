`validate_upload` now enforces the three rules, and ruff, ty and pytest all pass (20 tests).

- **Extension:** it must be `.pdf`, `.png` or `.csv`, in any case. A bad one is rejected with "file extension is not allowed".
- **Path separators:** a `/` or `\` in the filename is rejected, not stripped. The message is "filename must not contain a path separator".
- **Leading dot:** a name starting with `.` is rejected with "filename must not start with a dot".
- **Stored name:** the function returns the filename lowercased.
- **Check order:** size is checked first, then separators, then the leading dot, then the extension. A name like `.pdf` fails the leading-dot rule, not the extension rule.

I also fixed a bug in `extension_of` in `src/uploads/naming.py`. For a name with no dot, such as `pdf`, it returned the whole name as the extension, so `pdf` would have been accepted. It now returns `""` in that case. `validate_upload` was its only caller. The old `base_name` helper is no longer used by `validate_upload`. I left it in place.

I added tests to `tests/test_validation.py` in the existing style. They cover lowercasing, each allowed extension in mixed case, disallowed extensions, both separator kinds, and leading dots.

Running `uv run ty check` as-is picks up a parent directory outside this repo and reports 21 unrelated errors. It also can't resolve `uploads` because the repo config doesn't set a search path for ty. I scoped it instead: `uv run ty check --project . --extra-search-path src src tests`. I didn't change any config.
