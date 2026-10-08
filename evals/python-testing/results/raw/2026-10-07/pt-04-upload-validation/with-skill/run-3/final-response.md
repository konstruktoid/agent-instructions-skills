`validate_upload` now enforces all three rules and still raises `UploadRejected` for any failure, each with its own message. Pytest passes (17 tests), and `ruff check` and `ruff format --check` are clean. `ty` passes once it is told about `src`. A plain `uv run ty check` doesn't pass here.

- **Extension:** it must be `.pdf`, `.png` or `.csv`, in any case. Otherwise it raises "file extension is not allowed".
- **Path separator:** a filename containing `/` or `\` raises "filename must not contain a path separator". It is rejected as-is, not stripped.
- **Leading dot:** a filename starting with `.` raises "filename must not start with a dot".
- **Stored name:** the function returns the filename lowercased.

Checks run in that order: size, separator, leading dot, then extension.

I also changed `extension_of` in `src/uploads/naming.py`. For a name with no dot, such as `pdf`, it returned the whole name, which would have passed as an allowed extension. It now returns an empty string, so those names are rejected. Nothing else in the repo calls `extension_of`.

`validate_upload` no longer uses `base_name`, because separators are rejected instead of stripped. I left `base_name` in place.

I added parametrized tests to `tests/test_validation.py` covering each rejection and the case-insensitive acceptance.

Two things about `ty`:
- **No `src` path:** `uv run ty check` can't resolve `import uploads` because the repo's config doesn't tell `ty` about `src`. The existing test file has the same problem, so it isn't from my change. `uv run ty check --extra-search-path src src tests` passes. I left the config alone.
- **Parent project errors:** without the `src tests` arguments, `ty` also scans the parent project's scripts and reports 14 errors, none in this repo's code.

I haven't committed anything.
