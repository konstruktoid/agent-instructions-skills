I added `save_settings(path, settings)` to `app/settings.py`. A quick check wrote `{'b': 1, 'a': 2}` and got `{\n  "a": 2,\n  "b": 1\n}\n`, with no temp file left in the directory.

The function writes the JSON to a temporary file in the same directory, then renames it over `path`. A failed write therefore leaves any existing settings file intact, and the temp file is removed. Your instructions require that for a write that replaces a file.

I didn't add a test. I also didn't test the failure path, or a `path` whose directory doesn't exist.
