I added `save_settings(path, settings)` to `app/settings.py`. It writes the dict to `path` as JSON with `indent=2` and `sort_keys=True`, then adds a trailing newline. I didn't run it or any tests.
