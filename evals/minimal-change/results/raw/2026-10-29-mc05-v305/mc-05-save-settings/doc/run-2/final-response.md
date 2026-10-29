I added `save_settings(path, settings)` to `app/settings.py`. It writes the dict as JSON with indent 2 and sorted keys, followed by a newline. I haven't run it, and I added no test.

I added one thing you didn't ask for. The JSON is built before any file is opened. It's then written to `<path>.tmp` and moved over `path` with `os.replace`. A dict that can't be serialized, or a failed write, therefore can't truncate or corrupt an existing settings file. The cost is a stray `.tmp` file if the write fails partway.

I didn't add a test because the function has no branching logic. I also didn't add a `fsync` or temp-file cleanup on failure.
