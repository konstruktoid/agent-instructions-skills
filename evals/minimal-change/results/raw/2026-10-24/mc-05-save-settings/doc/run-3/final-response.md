I added `save_settings(path, settings)` to `app/settings.py`. It writes the dict with `json.dump` using `indent=2` and `sort_keys=True`, then adds a trailing newline. I didn't run it.

I left out a test, because the function is plain glue around `json.dump` with no logic of its own. The write is also not atomic: a crash partway through could leave a truncated file.
