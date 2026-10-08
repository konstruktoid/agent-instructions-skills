I couldn't find a `subprocess` call with `shell=True` anywhere in this workspace, so I haven't changed anything.

- I searched every file for `shell=True`, `subprocess`, `os.system` and `os.popen` and got no matches.
- The only Python files are `src/ledger/balance.py`, `src/ledger/client.py` and `tests/test_balance.py`. None of them start a process. `client.py` calls a `transport` function that's passed in, but it doesn't use a shell.

The call may be in another repo or branch, or in a file that isn't committed here. If you paste it or give me the path, I'll rewrite it. The fix usually looks like this:

```python
# Before: the shell parses the string, so a filename like "x; rm -rf ~" runs as a command
subprocess.run(f"tar -czf {archive} {src_dir}", shell=True)

# After: an argument list with no shell, so each value reaches the program as one argument
subprocess.run(
    ["tar", "-czf", archive, "--", src_dir],
    check=True,           # raise on non-zero exit instead of failing silently
    timeout=300,          # don't hang forever
)
```

Things to check when converting:
- **Use a list of arguments, not a string.** Without a shell, quoting isn't needed and characters like `;`, `$()` and backticks aren't treated as commands. If you have to split an existing string, use `shlex.split`, but never on untrusted input.
- **Put `--` before user-supplied paths** so a value starting with `-` isn't read as an option.
- **Replace shell features with Python:**
  - Pipes: use two `Popen` calls, or do the processing in Python.
  - Redirects: use `stdout=open(...)`.
  - Globs: use `glob.glob`.
  - `&&`: make sequential calls with `check=True`.
  - Environment variables: pass `env=`.
- **Capture output safely:** `capture_output=True, text=True` instead of backticks or `$(...)`.
