I added `save_settings(path, settings)` to `app/settings.py`, plus an `import os`. I ran it once with `{'b': 1, 'a': 2}`, and the output had sorted keys, indent 2 and a trailing newline.

The function builds the JSON text first, so data that can't be serialized fails before the file is touched. It then writes to `<path>.tmp` and swaps it in with `os.replace`. A failed or interrupted write leaves the existing settings file intact instead of truncating it. You didn't ask for this, but the project's minimal-change instructions say a write that could lose data keeps its safeguard.

I added no test, because the function has no branching logic. The one run above is the only check. The temp file is a fixed name, so two concurrent writers to the same path could collide. It also doesn't fsync, so a power loss could still lose the new contents.
