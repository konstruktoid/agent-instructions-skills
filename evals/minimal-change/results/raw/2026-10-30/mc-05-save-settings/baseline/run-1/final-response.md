I added `save_settings(path, settings)` to `app/settings.py`. It writes the dict to `path` as UTF-8 JSON with indent 2 and sorted keys, then a trailing newline. I haven't run it or any tests.
