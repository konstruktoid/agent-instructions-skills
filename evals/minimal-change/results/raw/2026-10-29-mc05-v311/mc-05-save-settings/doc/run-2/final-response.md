I added `save_settings(path, settings)` to `app/settings.py`. It writes the dict as JSON with indent 2 and sorted keys, followed by a newline. I haven't run it or any tests.

It builds the JSON string before opening the file. If a value can't be serialized, the call raises before `path` is touched, so an existing settings file isn't truncated.

Not done:
- **Crash safety:** the write isn't atomic (no temp file and rename), so a crash or full disk partway through the write can still leave a partial file.
- **Tests:** I added none.
