I added `save_settings(path, settings)` to `app/settings.py`. It writes the dict to `path` as UTF-8 JSON with `indent=2` and `sort_keys=True`, followed by a newline. I also added one test in `tests/test_settings.py` that checks the exact output. Both tests pass.

Skipped: I didn't add atomic write (temp file plus rename), so a crash mid-write could leave a truncated file. I also didn't add validation or error handling beyond what `open` and `json.dump` raise. A non-serializable value would raise `TypeError` after the file is already truncated.
