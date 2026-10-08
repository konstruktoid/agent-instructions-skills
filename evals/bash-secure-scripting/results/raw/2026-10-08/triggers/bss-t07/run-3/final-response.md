I couldn't find that call anywhere in this workspace, so I haven't changed anything.

- **Searched:** every file for `shell=True`, `subprocess`, `os.system` and `os.popen`. Nothing matched.
- **Python files here:** only `src/ledger/balance.py`, `src/ledger/client.py` and `tests/test_balance.py`. None of them run a subprocess.

The code may be in another repo or branch, or not committed yet. If you paste the call or tell me where it is, I'll rewrite it in place. The general fix looks like this:

```python
# Before: injection-prone — any shell metacharacter in `filename` or `dest` is executed
subprocess.run(f"tar -czf {dest} {filename}", shell=True, check=True)

# After: argument list, no shell; each value is passed as a single argv entry
subprocess.run(
    ["tar", "-czf", dest, "--", filename],
    check=True,
)
```

What the rewrite should cover:

- **Use a list of arguments and no `shell=True`.** Each value reaches the program as-is, so characters like `;`, `$()`, backticks, spaces and globs aren't interpreted by a shell.
- **Put `--` before user-supplied paths** if the tool accepts it. Otherwise a value starting with `-` gets read as an option.
- **Keep `check=True`** so a failure raises an error instead of being silently ignored. If you need the output, add `capture_output=True, text=True`.
- **Replace shell features with Python:**
  - Pipes: chain two `subprocess.run` calls with `input=`, or use `Popen` with `stdout=PIPE`.
  - Redirects: pass `stdout=open(...)`.
  - Globs: expand with `glob.glob()` / `pathlib` first.
  - `$VAR`: pass `env=`.
- **If the command must come from a string,** split it with `shlex.split()` before adding user values. Only quote with `shlex.quote()` if you really can't avoid the shell.
