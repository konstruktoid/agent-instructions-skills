I added `save_settings(path, settings)` to `app/settings.py`. It writes the dict as JSON with `indent=2` and `sort_keys=True`, then a trailing newline. It opens the file as UTF-8, the same way `load_settings` does.

`ruff check`, `ruff format --check` and `ty check` all pass on `app/settings.py`. I didn't write or run a test for it.

The repo-wide `ruff check .` reports 22 errors. The one I looked at is in an existing test file and is unrelated to this change. I left those alone.
