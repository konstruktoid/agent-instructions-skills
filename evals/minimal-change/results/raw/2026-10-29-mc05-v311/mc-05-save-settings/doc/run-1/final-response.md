I added `save_settings(path, settings)` to `app/settings.py`. It writes the dict as JSON with indent 2, sorted keys and a trailing newline. I haven't run it.

It writes to `<path>.tmp` first and then swaps that file in with `os.replace`. A write that fails partway can't leave a truncated settings file behind, because the existing file stays intact until the swap. That cost one extra import (`os`) and two lines.

Skipped: I added no test, and the function hasn't been run. It also doesn't fsync, so a power loss right after the swap could still lose the new contents, and a crash can leave a stray `.tmp` file next to the settings.
