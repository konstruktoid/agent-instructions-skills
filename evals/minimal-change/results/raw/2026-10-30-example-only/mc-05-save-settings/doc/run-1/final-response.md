I added `save_settings(path, settings)` to `app/settings.py`. It writes `json.dumps(settings, indent=2, sort_keys=True) + "\n"` to `path`.

The write goes through the existing `atomic_write` in `app/fsutil.py` rather than a plain `open(..., "w")`. A failed write therefore leaves the old settings file intact, as the minimal-change rules require.

I called it once with `{'b': 1, 'a': 2}` and got `{\n  "a": 2,\n  "b": 1\n}\n`. The existing test suite still passes.

I added no test for `save_settings`, since it has no logic of its own. I also didn't test the failure path, where the old file should stay intact.
