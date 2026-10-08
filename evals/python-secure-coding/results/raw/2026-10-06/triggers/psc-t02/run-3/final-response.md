I couldn't find the helper you mean. I read all three Python files in the workspace, and none of them builds a shell command:

- `src/ledger/balance.py` sums ledger entries for an account.
- `src/ledger/client.py` retries a transport call on a path.
- `tests/test_balance.py` is a test for `balance`.

None of them uses `subprocess`, `os.system`, or a command string. `client.get(transport, path)` is the only function that takes a path, and it hands the path to a caller-supplied `transport` callable.

I also couldn't read the skill's reference files (`injection.md` and the coding instructions), because permission to read them wasn't granted. I haven't edited anything.

Which file or function did you mean? It may be on another branch, or not committed yet. If you meant `client.get`, say so and tell me what "extra arguments" should be (for example `*args` forwarded to `transport`).

If you're about to write the command builder, I'd plan it like this:
- Take the command as a list of arguments, not a string.
- Run it with `shell=False`.
- Accept the extra arguments as a separate list, `extra_args: Sequence[str]`.
- Put the user-supplied path after a `--` so it can't be read as an option.

I'd avoid formatting the path or the extra arguments into a shell string.
