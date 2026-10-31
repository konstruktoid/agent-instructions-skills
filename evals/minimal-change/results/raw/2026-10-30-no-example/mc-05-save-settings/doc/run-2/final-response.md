I added `save_settings(path, settings)` to `app/settings.py`. It writes the dict as JSON with `indent=2` and `sort_keys=True`, followed by a newline. The tests pass (2 run).

The file is written to a temporary file in the same directory and then swapped in with `os.replace`. A failed write therefore can't truncate an existing settings file, and the temporary file is removed on failure.

I added one test in `tests/test_settings.py`. It checks the exact output text and that no temporary file is left behind.

Not checked: the failure path, meaning cleanup after an error mid-write. I didn't test it.
