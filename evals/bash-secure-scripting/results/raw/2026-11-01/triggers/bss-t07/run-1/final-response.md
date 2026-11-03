I couldn't find that call in this repo, so I haven't changed anything. A search for `shell=True`, `subprocess`, `os.system` and `os.popen` came back empty. The only Python files are `src/ledger/balance.py`, `src/ledger/client.py` and `tests/test_balance.py`, and none of them run a command.

If you paste the call or tell me where it is, I'll rewrite it. In general, the fix looks like this:

```python
# Before: any shell metacharacter in `name` or `dest` is run by the shell
subprocess.run(f"tar -czf {dest} {name}", shell=True)

# After: an argument list, no shell, so each value is passed to tar unchanged
subprocess.run(
    ["tar", "-czf", dest, "--", name],
    check=True,          # raise CalledProcessError on a non-zero exit
    timeout=300,         # don't hang forever
)
```

A few things to watch for when converting:

- **Pass each argument as its own list item.** Don't use `shlex.split()` on a formatted string, because the input has already been mixed into the command by then.
- **Put `--` before values that come from users** if the program supports it. That stops a value like `-rf` from being read as an option.
- **Rebuild shell features in Python.** Without a shell, pipes, `>` redirects, globs, `~` and `$VAR` no longer work:
  - Use `stdout=open(path, "wb")` instead of a redirect.
  - Chain two `Popen` objects instead of `|`.
  - Use `glob.glob()` instead of a wildcard.
  - Use `os.path.expanduser()` instead of `~`.
  - Pass `env=` instead of relying on `$VAR`.
- **If you really need a shell,** keep the shell code fixed and pass the values as positional arguments: `subprocess.run(["sh", "-c", 'cmd "$1" | other', "sh", value])`.
