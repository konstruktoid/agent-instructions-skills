`validate_upload` now enforces the three rules. pytest (18 tests), `ruff check` and `ty check src tests` all pass.

- **Checks, in order:**
  1. Size (unchanged).
  2. A `/` or `\` in the filename is rejected with "filename must not contain a path separator".
  3. A leading dot is rejected with "filename must not start with a dot".
  4. An extension other than `.pdf`, `.png` or `.csv` is rejected with "file extension is not allowed". The check ignores case, so `.PDF` is accepted.
- **Stored name:** it is the filename lowercased. The old code stripped directory parts instead of rejecting them, and that call is gone.
- **Extension helper:** `extension_of` in `src/uploads/naming.py` returned the whole name when there was no dot, so a file literally named `pdf` would have passed. It now returns an empty string in that case, which gets rejected.
- **ty config:** `ty` couldn't resolve `uploads` because only pytest knew about `src`. I added `[tool.ty.environment] extra-paths = ["src"]` to `pyproject.toml`. This was an existing problem and isn't related to your change.
- **Tests:** I added them in `tests/test_validation.py`. They cover accepted extensions in mixed case, bad extensions, both separator kinds and leading dots.
- **Bare `ty check`:** run with no paths, it reports about 20 more errors. They are all in `check_*.py` and `run_eval.py`, which sit outside this repo's `src` and `tests`. I left those alone.
