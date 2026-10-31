I added `save_settings(path, settings)` to `app/settings.py`. It writes the dict as JSON with indent 2 and sorted keys, followed by a newline. A quick manual run produced the expected output (`{"a": 2, "b": 1}` came out as sorted, indented JSON).

The write goes to a temporary file in the same directory and is then renamed over `path`, as the repo's minimal-change instructions require for writes that replace a file. If the write fails, the old file stays intact and the temporary file is removed. This uses only the standard library, and `os` and `tempfile` are the new imports.

I added no test. The only run was the manual check above, and I didn't test the failure path. Nothing else was left out.
