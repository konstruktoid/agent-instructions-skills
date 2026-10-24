I couldn't find that call in this workspace, so I haven't changed anything. The only Python files are `src/ledger/balance.py`, `src/ledger/client.py` and `tests/test_balance.py`. I searched them for `shell=True`, `subprocess`, `Popen` and `os.system`, and none of those appear.

The call may be in another repo or branch, or in a file that isn't committed yet. If you paste it or give me the path, I'll rewrite it. Here is the general fix in the meantime:

**Before (unsafe):** anything in `filename` or `dest` is read by the shell, so `; rm -rf ~` or `$(...)` would run as a command.
```python
subprocess.run(f"cp {filename} {dest}", shell=True)
```

**After:**
```python
subprocess.run(["cp", "--", filename, dest], check=True)
```

What changes:
- **The arguments are a list, with no shell.** Each item goes straight to the program as one argument, so spaces, quotes, `;` and `$()` in the values do nothing special. You don't need `shlex.quote`.
- **`--`** stops a value that starts with `-` from being read as an option (e.g. a filename like `-rf`), as long as the command supports it.
- **`check=True`** raises `CalledProcessError` when the command fails, so errors aren't silently ignored.
- **To capture output**, add `capture_output=True, text=True` and read `result.stdout`.
- **If the original used pipes, redirects or globs,** do those in Python instead:
  - Pipes: chain `subprocess.run(..., input=prev.stdout)`.
  - Redirects: use `stdout=open(path, "w")`.
  - Globs: expand them with `glob.glob()` and add the results to the list.

  Don't go back to `shell=True` for these.
- **For a fixed tool path**, pass the absolute path (e.g. `/usr/bin/cp`) or set a controlled `env=` so it doesn't depend on the caller's `PATH`.
