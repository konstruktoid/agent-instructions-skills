I couldn't find that call, so I haven't changed anything.

I searched the workspace for `shell=True`, `subprocess`, `os.system` and `Popen` and got no matches. The only Python files are:

- `src/ledger/balance.py`
- `src/ledger/client.py`
- `tests/test_balance.py`

The code may be in another repository or branch, or not committed yet. Send me the path or paste the call and I'll rewrite it there.

The rewrite will usually look like this:

```python
# Before: the shell parses the string, so a value like "x; rm -rf ~" runs as a command
subprocess.run(f"tool --input {path} --name {name}", shell=True)

# After: pass an argument list with no shell, so each value reaches the program as-is
subprocess.run(
    ["tool", "--input", str(path), "--name", name],
    check=True,
)
```

Also worth knowing:

- **`--` before untrusted values:** if a value can start with `-`, put `"--"` before it (where the tool supports that) so it isn't read as an option.
- **Pipes and redirects:** if the original uses `|`, `>` or `&&`, chain separate `subprocess.run` calls instead. Use `stdout=`/`stdin=` file handles or `input=` to move data between them.
- **Full paths:** use the full path to the program (or `shutil.which`) if `PATH` could be controlled by someone else.
- **`shlex.quote`:** only use it if you truly need a shell. The argument list is the better fix.
