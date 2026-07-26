All 8 tests pass and ruff is clean (the pre-existing `ty` unresolved-import error is unrelated to this change — it reproduces identically on the unmodified baseline).

Summary of changes to `src/uploads/validation.py`:
- Extension allow-list (`.pdf`, `.png`, `.csv`) — rejects otherwise.
- Rejects filenames with a path separator (`/` or `\`) or a leading dot.
- Returns the filename lowercased as the stored name.
- Each failure raises `UploadRejected` with a message naming the specific rule.

Added matching tests in `tests/test_validation.py` for each new rule (accept/reject cases) and fixed a pre-existing unsorted-import lint issue in that file along the way.
