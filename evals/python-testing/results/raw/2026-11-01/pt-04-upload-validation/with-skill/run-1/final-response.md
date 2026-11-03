`validate_upload` now enforces the three new rules, and all 21 tests pass under `uv run pytest`. `ruff check`, `ruff format --check` and `ty check` are clean, but `ty` only resolves `uploads` when given `--extra-search-path src`. I haven't committed anything.

- **Extension:** it must be `pdf`, `png` or `csv` in any case. A name with no dot at all (such as `pdf`) is also rejected, because `extension_of` returns the whole name when there is no dot.
- **Path separators and leading dot:** a `/` or `\` anywhere in the name, or a name starting with `.`, raises `UploadRejected`. Nothing is stripped or repaired. The old code stripped directories with `base_name`, and that import is gone from `validation.py`.
- **Stored name:** the function returns `filename.lower()`.
- **Messages:** each rule has its own message, matching the existing "upload is too large" style. They are "filename contains a path separator", "filename starts with a dot" and "file extension is not allowed". The checks run in order: size, separator, leading dot, extension.

I added parametrized tests in `tests/test_validation.py` for each rule's accept and reject paths, including backslashes, `../`, and names like `a.pdf.exe`.

I did not run the new tests against the old code to confirm they fail there.

A plain `uv run ty check` from the workspace also scans files outside the repo (`run_eval.py` and the scripts under `scripts/`). It fails on those, none of which I touched.

The changes are in `src/uploads/validation.py` and `tests/test_validation.py`.
