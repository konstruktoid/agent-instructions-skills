I added `save_settings(path, settings)` to `app/settings.py`. It writes the dict as JSON with indent 2, sorted keys and a trailing newline. A manual run printed the expected output for `{'b': 1, 'a': 2}`: `a` first, then `b`, with the newline at the end.

The repo's minimal-change instructions say a write that replaces an existing file must leave the old file intact if it fails. So the function writes to a temporary file in the same directory, flushes and fsyncs it, then swaps it over `path` with `os.replace`. If anything fails, it deletes the temporary file and re-raises the error. This adds `os` and `tempfile` imports from the standard library.

I didn't add a test, because the function is glue over `json.dump` and the repo has no test setup I could see. I only ran the one manual check, not the failure path, and the new file gets the temp file's default permissions (0600), not the usual umask-based ones.
