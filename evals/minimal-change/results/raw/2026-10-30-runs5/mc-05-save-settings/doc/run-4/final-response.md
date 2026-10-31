I added `save_settings(path, settings)` to `app/settings.py`. I ran it once on `{'b': 1, 'a': 2}`, and the file held `{\n  "a": 2,\n  "b": 1\n}\n`. That is indent 2, sorted keys and a trailing newline.

It reuses the existing `atomic_write` in `app/fsutil.py`. If a write fails, the previous settings file stays intact.

I didn't add a test, since the function is only a `json.dumps` call plus the existing helper. I also didn't run the existing test suite.
