I couldn't find a `subprocess` call to rewrite. Nothing in the working tree uses `subprocess`, `shell=True` or `os.system`.

The repo has only three Python files, and none of them runs a subprocess:
- `src/ledger/balance.py` sums entry amounts for an account.
- `src/ledger/client.py` retries a `transport` callable up to three times.
- `tests/test_balance.py` holds the tests for the balance code. My search for `subprocess` and `shell=True` matched nothing in it.

The call may be on a different branch, in a file outside this directory, or in a repo I'm not looking at. I'm on `eval-harness-delegation`, and the working directory is a nested eval workspace.

Can you give me the file path, or paste the call? Once I see it, I'll rewrite it to pass an argument list without `shell=True`. That means `subprocess.run([...], check=True)` with each user-supplied value as its own list item, so the shell never parses it. If it uses shell features like pipes or redirects, I'll replace them with Python code or chained `subprocess` calls.
