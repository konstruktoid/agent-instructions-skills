I added `save_settings(path, settings)` to `app/settings.py`. It writes the dict to `path` as UTF-8 JSON with `indent=2` and `sort_keys=True`, then a trailing newline.

I ran it once on `{'b': 1, 'a': 2}`. The file contained `'{\n  "a": 2,\n  "b": 1\n}\n'`, as expected.

I added no test, since the function is plain `json.dump` glue with no logic of its own. Writing is not atomic: if the process dies mid-write, the file can be left truncated. That is acceptable for a simple settings file but would need a temp-file-and-rename if that matters.
