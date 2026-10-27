I added `save_settings(path, settings)` to `app/settings.py`. It writes the dict with `json.dump` using `indent=2` and `sort_keys=True`, then a trailing newline. I didn't run it or any tests.

Skipped: I added no test, since the function is a direct `json.dump` call with no logic of its own. A failed write raises an `OSError` to the caller, and I didn't add error handling beyond that.
