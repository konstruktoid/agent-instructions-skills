I added `save_settings(path, settings)` to `app/settings.py`. It writes the dict as JSON with `indent=2` and `sort_keys=True`, then a trailing newline, using `json.dump` from the standard library. I didn't run it.

Skipped: I added no test, since the function is plain glue with no branching. It also doesn't write atomically, so a crash mid-write could leave a truncated file.
