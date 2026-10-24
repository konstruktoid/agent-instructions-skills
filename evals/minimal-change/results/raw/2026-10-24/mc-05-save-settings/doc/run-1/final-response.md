I added `save_settings(path, settings)` to `app/settings.py`. It writes the dict as JSON with `indent=2` and `sort_keys=True`, then a trailing newline. I also added one test, `SaveTest`, in `tests/test_settings.py`. It checks the exact output text, and both tests pass.

Skipped: I didn't add error handling. An `OSError` or a non-serializable value raises to the caller, and a failed write can leave a partial file. I also didn't add an atomic write (temp file then rename), which would prevent that.
