I added `save_settings(path, settings)` to `app/settings.py`. It writes the dict as JSON with indent 2, sorted keys and a trailing newline. Both tests pass, the new one and the existing `load_settings` test.

- **Atomic write:** the repo already has `atomic_write` in `app/fsutil.py`, so I reused it instead of writing a second version. It writes a temp file and renames it over the original, so a failed write leaves the old settings file intact.
- **Test:** I added one test in `tests/test_settings.py`. It saves `{"b": 1, "a": 2}` and checks the exact file contents.

Skipped: there is no input validation on `settings`. A value that isn't JSON-serializable raises `TypeError` before anything is written, so the old file is untouched. I did not test the failed-write path itself, since `atomic_write` is existing code.
