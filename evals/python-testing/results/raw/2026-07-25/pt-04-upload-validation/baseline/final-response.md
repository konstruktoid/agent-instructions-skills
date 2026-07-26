Done. Summary:

- `src/uploads/validation.py`: `validate_upload` now rejects filenames with a `/` or `\` (path separator), filenames starting with `.`, and extensions outside `.pdf`/`.png`/`.csv` — each with a distinct `UploadRejected` message naming the failed rule — and returns the filename lowercased as the stored name.
- `tests/test_validation.py`: added tests for the extension, path-separator, leading-dot, and lowercasing rules.
- `pytest` (6 passed) and `ruff check` (clean) both pass. Note: `ty check` fails, but that's pre-existing on the baseline commit too — it's picking up the wrong project root from a parent monorepo `pyproject.toml` and trying to resolve an unrelated file's `yaml` import; unrelated to this change.
