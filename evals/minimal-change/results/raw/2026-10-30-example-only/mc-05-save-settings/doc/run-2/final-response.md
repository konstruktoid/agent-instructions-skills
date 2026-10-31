I added `save_settings(path, settings)` to `app/settings.py`. It writes the dict as JSON with indent 2, sorted keys and a trailing newline. Both tests pass.

It goes through the existing `atomic_write` in `app/fsutil.py` rather than a plain `open(..., "w")`. That way a failed write leaves the old settings file intact, as the minimal-change instructions require.

I also added one test in `tests/test_settings.py` that checks the exact output text.

Skipped: failure behaviour (a failed write leaving the old file intact) isn't covered by a new test. I also didn't validate `settings`, so a non-JSON-serializable value raises `TypeError` before anything is written.
