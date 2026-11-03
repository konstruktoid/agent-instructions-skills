`validate_upload` now enforces the three new rules. Pytest passes (18 tests), `ruff check` and `ruff format --check` are clean, and `ty` passes once it's given `src` as a search path.

**What changed (`src/uploads/validation.py`):**
- **Separator:** a filename containing `/` or `\` is rejected with "filename contains a path separator". It's rejected as-is, not repaired. I stopped calling `base_name`, which only stripped `/` and would have repaired the name.
- **Leading dot:** a filename starting with `.` is rejected with "filename starts with a dot".
- **Extension:** the extension must be pdf, png or csv in any case, checked against `ALLOWED_EXTENSIONS` in `naming.py`. Otherwise it's rejected with "file extension is not allowed".
- **Stored name:** the returned name is the filename lowercased.
- **Order of checks:** size, then separator, then leading dot, then extension.

A name with no dot, such as `pdf`, is also rejected under the extension rule. `extension_of("pdf")` returns `"pdf"`, so without that guard it would have been accepted.

I added tests in `tests/test_validation.py` covering each rule and its message, mixed-case extensions, lowercasing, and the edge names above.

**`ty` and the repo root:** a plain `uv run ty check` reports 21 errors, all in `run_eval.py` and `scripts/` in the directories above this workspace. It scans up to that parent. Checking just `src tests` reports one error, "Cannot resolve imported module `uploads`", which is there without my changes too. `ty` doesn't read pytest's `pythonpath = ["src"]` setting. Adding `--extra-search-path src` clears it. I didn't change the project config.
