I added `save_settings(path, settings)` to `app/settings.py`. It writes the dict as JSON with indent 2 and sorted keys, then a trailing newline. It uses the standard library's `json.dump` and mirrors how `load_settings` opens files (UTF-8).

I didn't run it and didn't add a test, because it's a thin wrapper over `json.dump` with no logic of its own. The write isn't atomic, so a crash mid-write could leave a truncated file.
