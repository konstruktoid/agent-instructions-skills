I added `save_settings(path, settings)` to `app/settings.py`, and the two tests in `tests/test_settings.py` pass.

It writes the settings as JSON with an indent of 2, sorted keys and a trailing newline. It reuses the repo's `atomic_write` in `app/fsutil.py`, so a failed write leaves the old file in place instead of corrupting it.

I added one test that checks the exact output text.

Not covered: there is no test for a failed write, since that path belongs to `atomic_write`. `save_settings` also doesn't check that `settings` is a dict, because callers are inside the repo.
