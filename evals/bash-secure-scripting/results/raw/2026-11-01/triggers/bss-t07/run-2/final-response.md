I couldn't find that call, so nothing was changed. This workspace has only two Python source files, `src/ledger/balance.py` and `src/ledger/client.py`, plus `tests/test_balance.py`. None of them use `subprocess`, `shell=True`, `os.system` or `os.popen`. `client.py` gets its `transport` callable passed in from outside, so the subprocess call may be in code that isn't checked in here.

If you paste the call or tell me which file it's in, I'll rewrite it. The fix usually looks like this:

```python
# Before: a shell parses the string, so a value like "x; rm -rf ~" runs as a command
subprocess.run(f"pg_dump -h {host} -d {db} > {outfile}", shell=True)

# After: pass a list of arguments with no shell, and do the redirect in Python
import subprocess

with open(outfile, "wb") as out:
    subprocess.run(
        ["pg_dump", "-h", host, "-d", db],  # each value is one argument, never parsed by a shell
        stdout=out,
        check=True,        # raise if the command fails instead of carrying on silently
        timeout=300,
    )
```

What to watch for when converting:
- **Pipes, `&&`, globs and `~`** don't work without a shell. Chain separate `subprocess.run` calls, or connect them with `Popen(..., stdout=PIPE)`. Use `glob.glob()` and `os.path.expanduser()` in Python.
- **Values that start with `-`** can still be read as options by the program you're calling. Put `"--"` before positional values if the program accepts it.
- **If you really need a shell**, pass the values as positional arguments, not inside the string: `subprocess.run(["sh", "-c", 'cmd "$1"', "sh", value])`. `shlex.quote()` works too, but it's easier to get wrong.
- **Program name**: use an absolute path, or check it with `shutil.which()`, if `PATH` might not be trusted.
