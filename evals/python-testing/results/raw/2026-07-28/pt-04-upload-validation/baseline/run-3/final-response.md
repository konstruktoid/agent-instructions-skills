## Summary

`validate_upload` (`src/uploads/validation.py`) now enforces four rules, each raising `UploadRejected` with a distinct message:

1. **Size** (existing) — `"upload is too large"`
2. **Path separator** — rejects filenames containing `/` or `\` rather than stripping them — `"filename must not contain a path separator"`
3. **Leading dot** — `"filename must not start with a dot"`
4. **Extension** — must be `pdf`, `png`, or `csv` case-insensitively — `"file extension is not allowed"`

If all checks pass, it returns `filename.lower()` as the stored name.

Added `has_path_separator` and `starts_with_dot` helpers to `src/uploads/naming.py` (matching the module's existing role as home for filename helpers), and added 6 new tests in `tests/test_validation.py` covering case-insensitive extensions, rejected extensions, both slash styles, dotfiles, and lowercasing.

Verified: `pytest` (8 passed), `ruff check` (clean), and `ty check` (clean, run with `src` as root to match the project's `pythonpath` config — confirmed via `git stash` that running `ty` from the repo root fails identically on the pre-existing baseline, so that's not a regression from this change).
