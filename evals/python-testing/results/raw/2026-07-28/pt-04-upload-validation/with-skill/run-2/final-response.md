All done. Summary:

- `src/uploads/validation.py`: `validate_upload` now enforces four rules in order — size limit, no path separator (`/` or `\`), no leading dot, extension must be `.pdf`/`.png`/`.csv` case-insensitively — each raising `UploadRejected` with a distinct message, and returns the filename lowercased instead of stripping directories.
- `src/uploads/naming.py`: removed `base_name`, which is no longer used now that path separators are rejected rather than repaired.
- `tests/test_validation.py`: added 6 tests covering case-insensitive extensions, rejected extensions, both separator styles, leading-dot rejection, and lowercased storage name.

Verified: `ruff check`, `ruff format --check`, and `pytest` (8/8 passed) are all clean. `ty check` reports one pre-existing failure unrelated to this change (an unresolved `yaml` import in the outer eval-harness repo's `scripts/check_skills.py`, which `ty` picks up because it walks up the directory tree for `pyproject.toml` files) — confirmed present on the baseline commit before my edits too.
