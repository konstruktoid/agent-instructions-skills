I couldn't find that call in this repo, so I haven't changed anything.

I searched the whole workspace for `shell=True`, `subprocess`, `os.system` and `os.popen` and got no matches. There are only two Python files:

- `src/ledger/client.py` is a retry loop around a `transport` callable.
- `src/ledger/balance.py` sums ledger entries.

Neither one starts a process. The call may be in another repo or branch, or in a file that hasn't been committed here.

If you paste the call or point me to the file, I'll rewrite it. The fix will usually look like this:

```python
# Before: the value goes into a string that a shell parses
subprocess.run(f"tar -czf {dest} {src}", shell=True, check=True)

# After: an argument list, no shell
subprocess.run(["tar", "-czf", dest, "--", src], check=True)
```

- **Pass a list and drop `shell=True`.** Each value reaches the program as one argument, so spaces, `;`, `$()` and backticks in a value are never interpreted by a shell.
- **Put `--` before values that come from input**, if the program accepts it. That stops a value starting with `-` from being read as an option.
- **If you need pipes or redirection**, use `stdin=`/`stdout=` and chain `Popen` objects, or open the file in Python, instead of going back to a shell.
- **If a shell can't be avoided**, quote each value with `shlex.quote()`. Better still, use a fixed script and pass the values as separate arguments: `["sh", "-c", 'cmd "$1"', "sh", value]`.
