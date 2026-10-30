I added `save_settings(path, settings)` to `app/settings.py`. A quick run on `{'b': 1, 'a': 2}` wrote `{\n  "a": 2,\n  "b": 1\n}\n`, which is indent 2, sorted keys and a trailing newline.

It writes to a temporary file in the same directory and then swaps it in with `os.replace`. A failed write therefore can't truncate an existing settings file, and the temp file is removed on error. I included this because the minimal-change instructions say a replaced file must survive a failed write. It adds `os` and `tempfile` imports.

I didn't add a test, and I only ran the one check above. Temp files get default permissions (0600), so an existing file's mode isn't preserved.
