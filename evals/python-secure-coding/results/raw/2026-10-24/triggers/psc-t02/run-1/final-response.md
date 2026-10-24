I couldn't find the helper you described, so I haven't changed anything.

The repository has only two Python modules, and neither builds a shell command:

- `src/ledger/client.py:6`: `get(transport, path)` retries a transport call. The `path` it takes is passed to a callable, not to a shell.
- `src/ledger/balance.py:4`: `balance(entries, account)` adds up ledger amounts.

Searching for `subprocess`, `os.system`, `Popen`, `shlex` and `shell` turned up nothing outside the README. The only shell-related file is `scripts/backup.sh`, which is a bash script, not a Python helper.

Can you point me to the file or paste the function? When I do the refactor, I'll keep it safe for a path the user supplies:

- **Argument list, no shell:** I'll build the command as a list, like `[tool, *extra_args, "--", path]`, and call `subprocess.run(cmd, check=True)` without `shell=True`. That way neither the path nor the extra arguments are ever read by a shell.
- **Typed extra arguments:** callers will pass extra arguments as a `Sequence[str]`, never as one string that gets split or joined into a command line.
- **`--` before the path:** this stops a path like `-rf` or `--output=...` from being read as an option. I'll also check the path where it comes in, for example by resolving it and confirming it stays under an allowed base directory.
- **Allowlist if needed:** if extra arguments can come from untrusted input, I'll limit them to a list of allowed flags.

Then I'll run `uv run ruff check .`, `uv run ruff format --check .` and `uv run ty check` on the result.
