I added `save_settings(path, settings)` to `app/settings.py`. It writes the dict as JSON with indent 2 and sorted keys, plus a trailing newline. I haven't run it, and I didn't add a test.

It builds the JSON string before opening the file. If a value can't be serialized, the call raises before it touches `path`, so the existing settings file isn't truncated.

It still writes straight to `path`. A crash or full disk partway through the write could leave a partial file. Fixing that would take a temp file plus `os.replace`, which I left out because you didn't ask for it.
