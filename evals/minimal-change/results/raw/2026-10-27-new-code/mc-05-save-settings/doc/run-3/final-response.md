I added `save_settings(path, settings)` to `app/settings.py`. It writes the dict as JSON with indent 2, sorted keys and a trailing newline, using UTF-8 like `load_settings`. I also added one test, and the test suite passes.

Skipped:
- The write isn't atomic: a crash partway through could leave a truncated file. I didn't add a temp-file-and-rename step because the request didn't ask for one.
- There's no test for unserializable values or unwritable paths, since both just raise the standard errors.
