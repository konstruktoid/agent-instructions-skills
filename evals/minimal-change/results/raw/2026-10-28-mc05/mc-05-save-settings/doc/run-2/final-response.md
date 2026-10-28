I added `save_settings(path, settings)` to `app/settings.py`. I haven't run it, and I added no test.

It writes the dict as JSON with an indent of 2, sorted keys and a trailing newline. I added one safeguard you didn't ask for. It writes to `<path>.tmp` and then swaps it in with `os.replace`. A crash or a failed write therefore can't leave the real settings file truncated. The JSON is also built in memory before any file is opened, so an unserializable value fails before anything is written.

Not done: no test, since the function is glue with no branching. There is also no cleanup of a leftover `.tmp` file if the write fails partway, and no `fsync` before the replace.
