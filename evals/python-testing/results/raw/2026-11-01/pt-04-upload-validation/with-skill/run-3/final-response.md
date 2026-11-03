`validate_upload` now enforces the three new rules. All 22 tests pass, and `ruff check` and `ruff format --check` are clean.

`ty check` only passes with `--extra-search-path src`. Without it, `ty` can't resolve `uploads` (the existing test import fails too), because the repo's `pyproject.toml` has no `ty` config pointing at `src`. I left `pyproject.toml` alone. Running `ty` from the workspace root with no paths also picks up unrelated files in parent directories.

- **Extension:** it must be `.pdf`, `.png` or `.csv`, in any case. I added a guard in `extension_of` (`src/uploads/naming.py`): a name with no dot used to return the whole name, so a file called just `pdf` would have passed. It now returns an empty string and gets rejected.
- **Path separator or leading dot:** a `/` or `\` anywhere in the name, or a leading `.`, is rejected outright. `base_name` is no longer called from validation.
- **Stored name:** the filename lowercased.

Every failure raises `UploadRejected` with its own message, in this check order: "upload is too large", "filename must not contain a path separator", "filename must not start with a dot", "file extension is not allowed". A name that fails more than one rule reports only the first.

In `tests/test_validation.py` I added parametrized tests in the existing style:
- extensions accepted in mixed case
- bad extensions rejected, including no extension and `a.pdf.exe`
- both separator kinds rejected
- leading dot rejected
- stored name lowercased

I did not run the new tests against the old code to see them fail.
