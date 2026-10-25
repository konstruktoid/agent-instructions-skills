I couldn't find that call in this workspace, so I haven't changed anything.

I searched the whole tree for `shell=True`, `subprocess`, `os.system` and `os.popen` and got no matches. There are only two Python source files, and neither starts a process:
- `src/ledger/balance.py` adds up account entries.
- `src/ledger/client.py` retries a `transport` callable.

The call may be in another repo or branch, or not committed yet. If you paste it or tell me where it is, I'll rewrite it. The fix usually looks like this:

```python
# Before: the shell parses the formatted string, so a filename or user input
# containing ; $() ` or spaces can run other commands
subprocess.run(f"tar -czf {archive} {src_dir}", shell=True)

# After: an argument list with no shell, so each value reaches the program as one argument
subprocess.run(["tar", "-czf", archive, "--", src_dir], check=True)
```

The main points:
- **Pass a list and leave out `shell=True`.** Don't build a string and split it with `shlex.split`. That brings back the parsing problems.
- **Put `--` before positional arguments** when the program accepts it, so a value starting with `-` isn't read as an option.
- **Use `check=True`** so a failed command raises an error instead of being silently ignored. Add `capture_output=True, text=True` if you need the output.
- **Do shell features in Python.** Replace pipes with `input=` or by chaining `Popen`, redirects with `stdout=open(...)`, globs with `glob`/`pathlib`, and `$VAR` with `env=`.
- **Use a full path** for the program (e.g. `/usr/bin/tar`, or `shutil.which` checked once) if `PATH` could be controlled by someone else.
