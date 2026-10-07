I couldn't find the helper, so I haven't changed anything. Nothing in the workspace builds a shell command from a path.

- `src/ledger/client.py` has `get(transport, path)`, which only calls a `transport` callable.
- `src/ledger/balance.py` sums ledger entries.
- `scripts/backup.sh` and `cmd/parser.go` contain no command construction. The grep for `subprocess`, `os.system`, `shell`, `exec.Command` and `sh -c` found nothing relevant.

The helper may be on another branch, uncommitted in a different directory, or not yet added. Please give me its file path or paste it.

When I do refactor it, I'll avoid a shell string for the extra arguments. The caller would pass them as a `Sequence[str]`. The helper would build an argv list, `[program, *extra_args, path]`, and call `subprocess.run(argv, shell=False)`. A user-supplied path containing `;`, `$()` or spaces then stays a single argument. If the path could begin with `-`, I'd also put `--` before it, so the program doesn't read it as an option.

I also couldn't read the skill's `injection.md` and `python_coding_instructions.md` because file-read permission was denied. Everything above is from general practice, not those files. I'd need that permission to follow the skill's `ruff` and `ty` workflow exactly.
