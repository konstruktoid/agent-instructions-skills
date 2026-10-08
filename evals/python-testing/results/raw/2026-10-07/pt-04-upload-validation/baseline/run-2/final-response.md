`validate_upload` now enforces the three rules. The repo's own checks pass: pytest shows 17 passed, `ruff check` and `ruff format --check` are clean, and ty passes on `src` and `tests` once `src` is on its search path.

Plain `uv run ty check` fails. It reports 14 diagnostics, all in the parent project's `scripts/` (mostly a missing `yaml` import). Run on just `src` and `tests`, ty can't resolve `uploads` unless given `--extra-search-path src`. That error is there without my changes too. I didn't touch the config. Adding `src` to ty's search path in `pyproject.toml` would fix it if you want.

Each rule has its own message:
- **Path separator:** a `/` or `\` anywhere in the name raises `filename must not contain a path separator`.
- **Leading dot:** a name starting with `.` raises `filename must not start with a dot`.
- **Extension:** anything other than `.pdf`, `.png` or `.csv`, in any case, raises `file extension is not allowed`.
- **Stored name:** the return value is `filename.lower()`.

The size check still runs first and still says `upload is too large`.

I also fixed `extension_of` in `naming.py`. For a name with no dot, such as `pdf`, it returned the whole name, so a file called `pdf` would have passed the extension check. It now returns an empty string in that case. `base_name` is no longer used, since names with separators are rejected rather than stripped. I left it in place.

I added tests in `tests/test_validation.py` for each rule, including the no-dot, trailing-dot and `a.pdf.exe` cases.
