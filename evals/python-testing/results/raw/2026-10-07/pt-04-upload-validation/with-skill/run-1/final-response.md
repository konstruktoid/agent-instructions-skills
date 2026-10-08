`validate_upload` now enforces the three rules and still raises `UploadRejected` for any failure. I didn't make a commit.

- **Extension:** it must be `.pdf`, `.png` or `.csv` in any case. Anything else is rejected with "file extension is not allowed". That includes names with no extension, such as a file literally called `pdf`.
- **Filename:** it is rejected, not repaired, if it contains `/` or `\` ("filename contains a path separator") or starts with a dot ("filename starts with a dot").
- **Stored name:** the filename is returned lowercased. It no longer goes through `base_name`, since a path separator is now a rejection.
- **Messages:** the three new messages and the existing "upload is too large" are each distinct. The size check still runs first.

I added parametrized tests to `tests/test_validation.py` for the accepted and rejected cases of each rule.

**Checks:**
- `uv run pytest` passes (20 tests).
- `ruff check` and `ruff format --check` are clean.
- Bare `uv run ty check` reports errors from files outside this project, in a parent `scripts/` directory, and from a missing `yaml` import. It also can't resolve `uploads` because of the `src` layout. Scoped to this project with `uv run ty check --extra-search-path src src tests`, it passes.

I didn't run the new tests against the old code to confirm they fail there.
