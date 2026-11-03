I couldn't find that call in this repository, so I haven't changed anything.

I searched every file for `subprocess`, `shell=`, `os.system` and `os.popen` and got no matches. The repository has only two Python source files, and neither one runs a command:
- `src/ledger/client.py` has a retry loop around a `transport` function that is passed in.
- `src/ledger/balance.py` adds up ledger entries.

The call may be in another repository or on a branch that isn't checked out. If you paste it or tell me where it is, I'll rewrite it. The usual fix looks like this:

```python
# Before: user input is parsed by the shell, so it can inject extra commands
subprocess.run(f"tar -czf {archive} {src_dir}", shell=True)

# After: pass a list of arguments, so the shell never parses the input
subprocess.run(
    ["tar", "-czf", archive, "--", src_dir],
    check=True,           # raise if the command fails
    timeout=300,          # optional: so it can't hang forever
)
```

What to check when converting:
- **Split the command into a list yourself.** Don't use `shlex.split()` on a string that has user input already formatted into it, because the input can still add extra arguments.
- **Add `--` before arguments that come from users** when the command supports it. Otherwise a value starting with `-` is read as an option.
- **Rewrite shell features in Python.** Pipes become two `subprocess.Popen` calls connected with `stdout=PIPE`. `>` redirects become `stdout=open(...)`. Globs become `glob.glob()`. `$VAR` becomes `env={...}`.
- **Capture output** with `capture_output=True, text=True` if you need it, not backticks or `$(...)`.
