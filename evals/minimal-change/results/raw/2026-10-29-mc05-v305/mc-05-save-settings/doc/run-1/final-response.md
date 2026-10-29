I added `save_settings(path, settings)` to `app/settings.py`, plus the `os` import it needs. It writes JSON with `indent=2` and `sort_keys=True`, then a trailing newline. I haven't run it, and I added no test.

I made the write atomic. It writes to `<path>.tmp` and then calls `os.replace`, so a failed write can't leave a truncated settings file.

Skipped:
- **Tests:** none added, because the project has no test setup for this module.
- **Cleanup:** if the write fails, the `.tmp` file is left behind.
- **Durability:** there's no `fsync`, so the file isn't protected against a power loss mid-write.
