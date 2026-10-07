I searched the repo for the helper that builds a shell command from a path, and I can't find it. The only Python files are `src/ledger/client.py`, `src/ledger/balance.py` and `tests/test_balance.py`. None of them uses `subprocess`, `os.system` or shell strings. `client.get(transport, path)` takes a path but only passes it to a `transport` callable. `scripts/backup.sh` is shell, not Python.

I haven't changed anything. Can you tell me one of these?

- The file and function name of the helper. It may be on another branch or not committed yet.
- Whether you meant `client.get`, where "extra arguments" would mean something like `*args` or `**kwargs` forwarded to `transport`.

Once I have the helper, I'll make the argument list a sequence passed to `subprocess.run([...])` with `shell=False`. The caller's extra arguments then stay separate argv entries and are never joined into a shell string. If the path can start with `-`, I'll put `--` before it so it isn't read as an option.
