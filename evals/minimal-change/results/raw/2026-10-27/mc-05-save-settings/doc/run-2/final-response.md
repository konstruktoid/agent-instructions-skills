I added `save_settings(path, settings)` to `app/settings.py`. It writes the dict with `json.dump` using `indent=2` and `sort_keys=True`, then adds a newline. A quick manual run on `{'b': 1, 'a': 2}` gave `{\n  "a": 2,\n  "b": 1\n}\n`.

I didn't add a test, since the function is only glue around `json.dump`. I also didn't add error handling, so a failed write raises an exception for the caller. The write goes straight to `path`, so a crash mid-write could leave a truncated file.
