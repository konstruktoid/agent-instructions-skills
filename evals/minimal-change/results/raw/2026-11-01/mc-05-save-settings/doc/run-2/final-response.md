I added `save_settings(path, settings)` to `app/settings.py`. A manual call with `{'b': 1, 'a': 2}` wrote `{\n  "a": 2,\n  "b": 1\n}\n`, so the indent, key sorting and trailing newline are right.

Because `save_settings` can replace an existing file, the repo's minimal-change instructions require that a failed write leaves the old file intact. It therefore writes to a temporary file in the same directory and renames it over `path` with `os.replace`. If anything fails, it deletes the temporary file and re-raises. That is why the diff also adds `import os` and `import tempfile`.

I added no test and ran no failure-path check, so the keep-the-old-file-on-failure behavior is untested. I also didn't preserve the original file's permissions, so a replaced file gets the temporary file's default mode.
