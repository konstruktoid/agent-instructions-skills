All 8 tests pass, ruff check and ruff format check are clean. The `ty check` failure is pre-existing and unrelated (it's an import error in a script outside this repo, reproduced identically on the pre-change baseline via `git stash`).

Summary of changes:
- `src/uploads/validation.py`: `validate_upload` now rejects (rather than repairs) filenames containing `/` or `\`, rejects filenames starting with `.`, validates the extension against `.pdf`/`.png`/`.csv` case-insensitively, and returns the filename lowercased. Each failure raises `UploadRejected` with a distinct, rule-specific message.
- `src/uploads/naming.py`: removed the now-unused `base_name` helper (validation no longer repairs paths, it rejects them).
- `tests/test_validation.py`: added coverage for case-insensitive extensions, disallowed extensions, both path-separator styles, dot-prefixed filenames, and the lowercased stored name.
