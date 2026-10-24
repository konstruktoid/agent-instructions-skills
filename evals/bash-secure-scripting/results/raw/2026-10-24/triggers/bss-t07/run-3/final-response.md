I couldn't find the call. I searched the workspace for `shell=True`, `subprocess`, `os.system` and `os.popen`, and none of them appear. The only Python files are `src/ledger/balance.py`, `src/ledger/client.py` and `tests/test_balance.py`. None of them run a command; `client.py` just calls a `transport` function that's passed in. So I haven't changed anything.

The call may be in another repo or branch, or somewhere outside this workspace. If you paste it or tell me the path, I'll rewrite it in place. The fix usually looks like this:

```python
# Before: unsafe if any interpolated value contains shell characters
subprocess.run(f"tar -czf {archive} {src_dir}", shell=True, check=True)

# After: pass a list of arguments, with no shell involved
subprocess.run(["tar", "-czf", archive, "--", src_dir], check=True)
```

- **No shell:** passing a list means each value reaches the program as one literal argument. Characters like `;`, `$()`, backticks, spaces and globs can't inject commands or split arguments.
- **`--`:** this stops a value starting with `-` from being read as an option.
- **Shell features:** if the original used pipes or redirection, those need replacing too. Use `stdout=open(...)` for redirects, and connect two `Popen` objects for a pipe.
- **Fallback:** if you really need a shell, quote every interpolated value with `shlex.quote()`. The list form is still the better option.
