I added `save_settings(path, settings)` to `app/settings.py`. It writes the dict as JSON with indent 2, sorted keys and a trailing newline. I ran it once with `{'b': 1, 'a': 2}` and the file contained `{\n  "a": 2,\n  "b": 1\n}\n`.

The write goes through the existing `atomic_write` in `app/fsutil.py` (reuse-ladder rung 2). A failed write therefore leaves the old settings file intact, and I didn't write a second version of that logic.

I added no test, only that one manual run, because the function is glue with no logic of its own. I didn't test the failure path.
