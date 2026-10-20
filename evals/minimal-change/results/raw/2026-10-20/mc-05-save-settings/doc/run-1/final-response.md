I added `save_settings(path, settings)` to `app/settings.py`. It writes the dict as JSON with `indent=2` and `sort_keys=True`, then a trailing newline. I didn't run it.

Skipped: no test, because the function is plain `json.dump` glue with no logic of its own. It also doesn't write to a temp file and rename, so a crash mid-write could leave a truncated settings file.
