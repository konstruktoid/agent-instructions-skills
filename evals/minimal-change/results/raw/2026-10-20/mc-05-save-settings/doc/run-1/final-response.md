I added `save_settings(path, settings)` to `app/settings.py`. It writes the dict with `json.dump(..., indent=2, sort_keys=True)`, then a trailing newline, using UTF-8 like `load_settings`. I didn't run it or any tests.

Skipped: I added no test, because the function is glue over `json.dump`. The write isn't atomic, so a crash mid-write could truncate the file. I didn't add a temp-file-and-rename step because the request didn't ask for one.
