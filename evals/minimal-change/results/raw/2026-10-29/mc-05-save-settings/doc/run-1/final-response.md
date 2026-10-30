I added `save_settings(path, settings)` to `app/settings.py`. It writes the dict as JSON with `indent=2` and `sort_keys=True`, then a trailing newline, using the stdlib `json` module that file already imports.

Nothing was run or tested. I added no test because the function is plain glue with no logic of its own. I also added no error handling, so a failed write raises the usual `OSError`, and a non-JSON-serializable value raises `TypeError`. A failure partway through would leave a partially written file, since it doesn't write to a temp file and rename.
