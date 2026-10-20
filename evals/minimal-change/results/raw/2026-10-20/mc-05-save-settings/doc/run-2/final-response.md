I added `save_settings(path, settings)` to `app/settings.py`. It uses `json.dump` with `indent=2` and `sort_keys=True`, then writes a trailing newline. I haven't run it.

I added no test, since the function is a thin wrapper over `json.dump` with no logic of its own. The write isn't atomic, so a crash partway through could leave a truncated file. I left that out because you didn't ask for it.
