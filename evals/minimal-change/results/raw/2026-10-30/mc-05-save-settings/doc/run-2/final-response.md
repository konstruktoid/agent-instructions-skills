I added `save_settings(path, settings)` to `app/settings.py`. It writes sorted-key JSON with an indent of 2 and a trailing newline. The tests pass.

The function reuses the existing `atomic_write` in `app/fsutil.py`. That helper writes a temp file in the same directory and renames it over the target, so a failed write leaves any existing settings file as it was.

I also added one test in `tests/test_settings.py` that checks the exact output text.

Skipped: no test for the failed-write path. That behaviour belongs to `atomic_write`, which I reused as it was.
