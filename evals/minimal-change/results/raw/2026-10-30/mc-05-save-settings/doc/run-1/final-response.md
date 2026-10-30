I added `save_settings(path, settings)` to `app/settings.py`. It writes JSON with `indent=2` and `sort_keys=True`, then a trailing newline. I haven't run it or any tests.

The repo's minimal-change rules say a write that replaces an existing file must leave the old file intact if it fails. So the function writes to a temp file in the same directory and then swaps it in with `os.replace`. If the write fails, it deletes the temp file and re-raises.

Skipped: no test added, and the function hasn't been exercised.
