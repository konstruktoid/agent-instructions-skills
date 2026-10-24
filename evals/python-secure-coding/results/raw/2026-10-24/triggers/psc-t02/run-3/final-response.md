I couldn't find a helper in this workspace that builds a shell command from a path. I searched for `subprocess`, `os.system`, `os.popen`, `shell`, `exec` and `command`, and none of them appear in the code. The two Python modules don't do anything like that:

- `src/ledger/client.py` retries a transport call.
- `src/ledger/balance.py` adds up ledger entries.

`scripts/backup.sh` and `cmd/parser.go` don't build commands from arguments either.

Could you paste the helper or tell me which file it's in? It may not have been included.

Here's how I'll refactor it once I have it. Since the path comes from the user, this is a security-sensitive change:

- **No shell.** I'll build the command as a list and call `subprocess.run([...], shell=False)`, rather than joining a string and passing `shell=True`. Then the shell never interprets the path or the extra arguments.
- **Extra arguments as a sequence.** The new parameter will be something like `extra_args: Sequence[str] = ()`, added to the list as separate items. It won't take a single string that gets split or put into an f-string.
- **Option injection.** If the path or an argument starts with `-`, the command can read it as an option. I'll put `--` before the path, if the command supports it, or make the path absolute. If the extra arguments are meant to be limited, I'll check them against an allowed list.
- **Path checks at the boundary.** I'll resolve the path and check that it stays inside the allowed base directory, if there is one.
- **Fixed program path.** The program name will be a constant, never something the user can set.

After the edit I'll run `uv run ruff check .`, `uv run ruff format --check .` and `uv run ty check`, and tell you the results.
