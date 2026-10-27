I added `save_settings(path, settings)` to `app/settings.py`. It writes the dict as JSON with indent 2 and sorted keys, then a newline. I also added one test in `tests/test_settings.py` that checks the exact file contents. The test suite passes (2 tests).

- **Skipped:** The write is not atomic, so a crash partway through could leave a truncated file. A temp-file-and-rename write would fix that if you need it.
- **Not checked:** I added no validation of `settings`. Non-JSON-serializable values raise `TypeError`, and the file may already be truncated by then.
