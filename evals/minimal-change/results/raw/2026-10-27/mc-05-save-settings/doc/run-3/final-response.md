I added `save_settings(path, settings)` to `app/settings.py`, and the tests pass (2 run, both OK). It writes the dict to `path` as JSON with indent 2 and sorted keys, then a newline. I also added one test in `tests/test_settings.py` that checks the exact file contents.

Skipped: I added no error handling beyond what `open` and `json.dump` already raise, and a failed write can leave a partial file. An atomic write via a temp file wasn't requested.
