I added `save_settings(path, settings)` to `app/settings.py`. It writes the dict as JSON with `indent=2` and `sort_keys=True`, followed by a newline. I haven't run it, and I added no test.

The function serializes first, then writes to `<path>.tmp` and swaps it in with `os.replace`. A failed or interrupted write therefore can't truncate or corrupt the existing settings file. The cost is one extra import (`os`) and two extra lines compared with a plain `open(path, "w")`.

Left out: the temp file isn't fsynced, so a power loss could still lose the newest write. Concurrent writers to the same path would also share one temp name.
