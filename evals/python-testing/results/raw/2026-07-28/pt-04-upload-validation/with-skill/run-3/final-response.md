Done. Summary of changes:

- **`src/uploads/validation.py`**: `validate_upload` now enforces, in order: filename must not contain `/` or `\`; filename must not start with `.`; extension must be `.pdf`/`.png`/`.csv` case-insensitively (reusing `ALLOWED_EXTENSIONS`/`extension_of` from `naming.py`); size limit. Each failure raises `UploadRejected` with a distinct message. The stored name returned is now `filename.lower()` (dropped the old `base_name` repair-by-stripping-path behavior, since path separators are now rejected outright).
- **`tests/test_validation.py`**: added tests for case-insensitive extensions, unsupported extensions, path-separator rejection (both slash types), dot-prefixed filename rejection, and lowercased stored name.

Verified: `pytest` — 11 passed; `ruff check` and `ruff format --check` — clean. `ty check` fails, but that's pre-existing on the unmodified baseline too — it mis-resolves its project root up to the enclosing meta-repo (`agent-instructions-skills`) and chokes on an unrelated file (`scripts/check_skills.py` importing `yaml`), unrelated to this workspace or change.
