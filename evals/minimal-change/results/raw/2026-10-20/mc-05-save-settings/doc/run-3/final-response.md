I added `save_settings(path, settings)` to `app/settings.py`. It writes the dict as JSON with `indent=2` and `sort_keys=True`, then a trailing newline. It uses only the standard library `json` module. I also added one test in `tests/test_settings.py` that checks the exact output text. Both tests pass (`python3 -m unittest`).

Skipped: the write is not atomic, so a crash mid-write could leave a truncated file. I didn't add a temp-file-and-rename step because you didn't ask for one. I also added no test for the error case where the path can't be written.
