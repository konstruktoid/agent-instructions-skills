I added `save_settings(path, settings)` to `app/settings.py`. It writes the dict as JSON with an indent of 2 and sorted keys, followed by a trailing newline.

I ran it once on `{'b': 1, 'a': 2}`. The output file had `a` before `b`, indented by 2 spaces. I didn't run any other tests.
