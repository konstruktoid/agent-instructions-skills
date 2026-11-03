`validate_upload` now applies the three new rules, and ruff, the format check and pytest all pass (18 tests).

`ty` needs a flag to pass. Plain `uv run ty check` fails in two ways. It walks up into the parent eval directory and reports 21 errors in files that aren't part of this repo. When scoped to `src tests` it can't resolve `uploads`, because the `pythonpath = ["src"]` setting in `pyproject.toml` is pytest-only. `uv run ty check --extra-search-path src src tests` passes. I left the config alone, but adding a `[tool.ty]` section pointing at `src` would make the plain command work.

I also fixed a bug in `uploads/naming.py`. `extension_of("pdf")` returned `"pdf"` because it had no dot to split on, so a file with no extension at all would have counted as a valid `.pdf`. It now returns `""` in that case.

What `validate_upload` does now, in order:
1. If the size is over the limit, it raises "upload is too large" (unchanged).
2. If the name contains `/` or `\`, it raises "filename must not contain a path separator". The name is rejected, not repaired.
3. If the name starts with a dot, it raises "filename must not start with a dot".
4. If the extension, compared in lowercase, isn't `pdf`, `png` or `csv`, it raises "file extension is not allowed".
5. Otherwise it returns the lowercased filename.

Each failure raises `UploadRejected` with its own message.

`base_name` in `uploads/naming.py` is no longer called, since names with separators are now rejected. I left it in place. I added tests for each rule, including mixed-case extensions, both separator types, leading dots, and names with no extension or a trailing dot.
