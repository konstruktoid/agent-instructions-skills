I added `save_settings(path, settings)` to `app/settings.py`. It writes the dict with `json.dump` using `indent=2` and `sort_keys=True`, then adds a trailing newline. I ran it once on `{'b': 1, 'a': 2}` and the file contained `{\n  "a": 2,\n  "b": 1\n}\n`.

It uses the standard library `json` module, which the file already imports. It writes UTF-8, the same as `load_settings`.

I didn't add a test, and it doesn't create missing directories, which you didn't ask for. If the write fails partway, the existing file could be left truncated. A write-to-temp-then-rename would prevent that, but I left it out as beyond the request.
