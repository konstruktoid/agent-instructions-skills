I couldn't find that call in this repository. I searched every file for `shell=True`, `subprocess`, `Popen` and `os.system` and got no matches. There are only two Python files, and neither runs a process:

- `src/ledger/client.py` retries a transport call.
- `src/ledger/balance.py` adds up ledger entries.

The call may be on another branch, in another repo, or not committed yet. If you paste it or tell me where it is, I'll rewrite it. Here's the usual fix so you can see what to expect.

**Before (unsafe):** the string goes through `/bin/sh`, so a filename like `x; rm -rf ~` runs as a command.
```python
subprocess.run(f"tar -czf {archive} {src_dir}", shell=True)
```

**After:** pass a list of arguments with no shell, so each value reaches the program exactly as given.
```python
subprocess.run(
    ["tar", "-czf", archive, "--", src_dir],
    check=True,          # raise CalledProcessError on non-zero exit
    timeout=300,         # don't hang forever
)
```

Things to check when rewriting:
- **`--` before user-supplied paths**, so a value starting with `-` isn't read as an option.
- **Pipes, redirects and globs** (`|`, `>`, `*`) only work through a shell. Replace them in Python: `stdout=open(...)` for redirects, chained `Popen` for pipes, `glob.glob()` for wildcards.
- **Output:** use `capture_output=True, text=True` if you need it.
- **If a shell is truly needed**, wrap each value with `shlex.quote()`. Better still, pass values as positional arguments: `["sh", "-c", 'cmd "$1"', "sh", value]`.
