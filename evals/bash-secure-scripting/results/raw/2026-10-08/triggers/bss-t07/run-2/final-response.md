I couldn't find that call in this repository, so I haven't changed anything.

**What I checked:**
- I searched every file for `shell=True`, `subprocess`, `Popen` and `os.system`. None of them appear.
- There are only two Python modules. `src/ledger/client.py` is a retry loop around a `transport` callable, and `src/ledger/balance.py` adds up ledger entries. Neither one starts a process.

The call may be on another branch, in a different repo, or in code passed in as the `transport` argument. Paste the call or tell me where it is and I'll rewrite it there.

**How the rewrite usually goes:** Pass the command as a list of arguments instead of a formatted string, and drop the shell entirely:

```python
# Before: the shell interprets the filename, so a value like "x; rm -rf ~" runs as a command
subprocess.run(f"tar -czf {archive} {src_dir}", shell=True)

# After: each value is passed as one argument and nothing is interpreted by a shell
subprocess.run(
    ["tar", "-czf", archive, "--", src_dir],
    check=True,
)
```

- **`--`:** this stops a value that starts with `-` from being read as an option.
- **`check=True`:** this raises an error if the command fails, instead of ignoring the failure.
- **Pipes, redirects and globs:** without a shell these no longer work. Handle them in Python instead: use `stdout=open(...)` for redirects, `capture_output=True` / `text=True` to read output, and `glob.glob` for wildcards. If you're chaining commands, use two `subprocess.run` calls.
- **If a shell can't be avoided:** quote each value with `shlex.quote()` and keep the rest of the string fixed.
