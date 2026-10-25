I couldn't find that call in this repo, so I haven't changed anything.

I searched the whole workspace for `shell=True`, `subprocess`, `os.system` and `os.popen` and got no matches. The only Python files are:

- `src/ledger/client.py`, a retry loop around a `transport` callable passed in by the caller
- `src/ledger/balance.py`, which sums ledger entries
- `tests/test_balance.py`

Neither source file runs a process. The `transport` passed into `client.get()` might shell out, but that code lives somewhere else.

If you paste the call or tell me which repo or file it's in, I'll rewrite it there. The fix usually looks like this:

```python
# Before: a value containing ; $( ) or spaces gets interpreted by the shell
subprocess.run(f"tar -czf {archive} {src_dir}", shell=True, check=True)

# After: an argument list goes straight to exec, so no shell parses it
subprocess.run(
    ["tar", "-czf", archive, "--", src_dir],
    check=True,
)
```

The rewrite generally comes down to these points:

- **Pass a list and drop `shell=True`.** Each value becomes one argument exactly as written, so `;`, `$(...)`, globs and spaces aren't interpreted.
- **Put `--` before values that could start with `-`**, if the tool supports it, so they can't be read as options.
- **Keep `check=True`** (or check `returncode`), and add `timeout=` if the command could hang.
- **Replace shell features with Python:**
  - pipes become two `Popen` calls chained through `stdout=PIPE`
  - redirects become `stdout=open(...)`
  - `$VAR` becomes `env={...}`
  - `cd x &&` becomes `cwd=x`
- **If you really need a shell**, quote each value with `shlex.quote()`. Better still, pass the values as positional arguments: `["sh", "-c", 'tar -czf "$1" -- "$2"', "sh", archive, src_dir]`.
