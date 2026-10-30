I added `save_settings(path, settings)` to `app/settings.py`. It writes sorted-key JSON with an indent of 2 and a trailing newline. A quick manual run on `{'b':1,'a':2}` produced `{\n  "a": 2,\n  "b": 1\n}\n`.

The repo's minimal-change instructions say a write that replaces an existing file must leave the old one intact if it fails. So it writes to a temporary file in the same directory and then renames it over `path` with `os.replace`. If the write fails, it deletes the temporary file and re-raises. That is why the change adds `os` and `tempfile` imports and is longer than a plain `json.dump`.

I added no test, and I did not check the failure path (old file kept after a failed write). I also did not check file permissions: a temp-file write may give the file different permissions than an existing `path` had.
