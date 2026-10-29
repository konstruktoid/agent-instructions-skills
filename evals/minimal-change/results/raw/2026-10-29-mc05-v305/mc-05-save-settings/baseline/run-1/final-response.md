I added `save_settings(path, settings)` to `app/settings.py`. It writes the dict as JSON with indent 2 and sorted keys, followed by a newline. It opens the file as UTF-8, like `load_settings` does.

I ran it once with `{'b': 1, 'a': 2}`. The file contained `{\n  "a": 2,\n  "b": 1\n}\n`, as expected. I didn't run any other tests.
