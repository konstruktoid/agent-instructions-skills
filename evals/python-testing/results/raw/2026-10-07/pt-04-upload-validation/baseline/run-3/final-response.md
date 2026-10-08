`validate_upload` now enforces the three rules, and ruff, ty and pytest (21 tests) all pass. Each rule raises `UploadRejected` with its own message:

- **Size:** "upload is too large", unchanged.
- **Path separator:** "filename contains a path separator", for `/` or `\`. The name is rejected rather than stripped.
- **Leading dot:** "filename starts with a dot".
- **Extension:** "file extension is not allowed". `.pdf`, `.png` and `.csv` pass in any case.
- **Stored name:** the function now returns the lowercased filename, e.g. `Report.PDF` becomes `report.pdf`.

I also changed `extension_of` in `src/uploads/naming.py`. It used to return the whole name when there was no dot, so a file literally called `pdf` would have passed. It now returns an empty string in that case.

`base_name` is no longer called by `validate_upload` and is now unused, since rejecting replaces repairing. I left it in place.

I added tests to `tests/test_validation.py` for each rule, including case variants, double extensions, both separator kinds and the lowercase result.

Plain `ty check` picked up unrelated scripts in a parent directory and reported errors there. I ran it as `ty check --extra-search-path src src tests`, which passes. The same command also passed before my changes.
