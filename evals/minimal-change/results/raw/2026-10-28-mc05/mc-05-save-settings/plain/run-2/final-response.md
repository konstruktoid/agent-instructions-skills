I added `save_settings(path, settings)` to `app/settings.py`. I haven't run it or added tests.

It opens `path` for writing as UTF-8, like `load_settings` does. It dumps the dict as JSON with `indent=2` and `sort_keys=True`, then writes a trailing newline.
