I couldn't find the helper you described, so I haven't changed anything.

What I checked:

- **Python files in the workspace:** there are two, `src/ledger/client.py` and `src/ledger/balance.py`. The only helper is `get(transport, path)` in `src/ledger/client.py:6`. It passes `path` to a `transport` callable and retries up to 3 times. It doesn't build a shell command.
- **Search:** I searched the whole repo for `subprocess`, `os.system`, `popen`, `exec` and `shell`. The only matches were two lines of prose in `README.md`.
- **Other files:** there's a shell script at `scripts/backup.sh` and a Go file at `cmd/parser.go`. If you meant one of those, it isn't Python. I'd treat it as a separate change.

Could you tell me which file the helper is in, or paste it? When I refactor it, I'd do it this way:

- Build the command as an argument list (`[cmd, *extra_args, "--", path]`) and run it with `subprocess.run(..., shell=False)`, never as a joined string.
- Take the extra arguments as a `Sequence[str]` and check them against an allowlist of permitted flags, so a caller can't sneak in an option like `--output=/etc/...`.
- Put `--` before the user-supplied path so a path starting with `-` can't be read as a flag. Resolve the path and check it stays inside its allowed base directory.

Or, if you meant to make `get()` in `client.py` accept extra arguments and pass them to `transport`, I can do that instead.
