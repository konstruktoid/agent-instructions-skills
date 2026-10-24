I added `save_settings(path, settings)` to `app/settings.py`. It writes the dict as JSON with `indent=2` and `sort_keys=True`, then a trailing newline. I also added one test in `tests/test_settings.py` that checks the exact file contents. Both tests (the new one and the existing load test) pass.

Left out: the function does no validation and has no error handling of its own. It opens the file for writing directly, so a failed write can leave a partial file, and it doesn't create missing parent directories. The test run also created untracked `__pycache__` directories.
