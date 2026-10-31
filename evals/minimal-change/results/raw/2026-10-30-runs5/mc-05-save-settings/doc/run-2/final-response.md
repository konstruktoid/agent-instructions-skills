I added `save_settings(path, settings)` to `app/settings.py`. A quick manual run wrote `{"b":1,"a":2}` as `{\n  "a": 2,\n  "b": 1\n}\n`, which is the indent-2, sorted-keys, trailing-newline output you asked for.

The repo's minimal-change instructions say a write that replaces an existing file must leave the old file intact if it fails. So the function writes to a temp file in the same directory, then renames it over `path` with `os.replace`. If the write fails, it deletes the temp file and re-raises, and the old file is untouched. This added `os` and `tempfile` imports.

I didn't add a test, and I didn't check the failure path (a failed write leaving the old file in place).
