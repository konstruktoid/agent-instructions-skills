I added `save_settings(path, settings)` to `app/settings.py`. It writes the dict as JSON with indent 2 and sorted keys, followed by a newline. I haven't run it, and I didn't add a test.

It builds the JSON string before opening the file. That way a value that can't be serialized raises an error without truncating the existing settings file.

Skipped:
- **No atomic write:** a crash or full disk partway through the write can still leave a partial file. A temp file plus `os.replace` would fix that, but you didn't ask for it.
- **No test:** none was required, and the function has no branching logic.
