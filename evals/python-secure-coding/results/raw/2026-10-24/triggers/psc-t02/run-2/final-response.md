I couldn't find the helper you mean, so I haven't changed any code. The workspace has only three Python files, and none of them build a shell command:

- `src/ledger/client.py`: `get(transport, path)` retries a transport call up to `MAX_ATTEMPTS` times. It takes a path, but it doesn't run anything in a shell.
- `src/ledger/balance.py`: sums ledger entry amounts for one account.
- `tests/test_balance.py`: tests for the balance function.

There's no `subprocess`, `os.system`, or `shell=True` anywhere. Could you paste the helper or tell me where it lives? It may be in a file that isn't in this workspace.

In this session I can read and search files but can't edit them or run commands. So once I have the code, I'll write out the refactored version for you to apply, and you'd need to run `uv run ruff check .`, `uv run ruff format --check .` and `uv run ty check` yourself.

If the helper does build a shell string from a user-supplied path, here's the safe way to add extra arguments:

```python
import subprocess
from collections.abc import Sequence
from pathlib import Path


def run_tool(path: str | Path, extra_args: Sequence[str] = ()) -> subprocess.CompletedProcess[str]:
    """Run ``tool`` on *path* with optional extra arguments, without a shell."""
    target = Path(path)
    if not target.is_file():
        raise ValueError(f"not a file: {target}")
    argv = ["tool", *extra_args, "--", str(target)]
    return subprocess.run(argv, capture_output=True, text=True, check=True)  # noqa: S603 - argv list, no shell
```

- **Pass a list and no `shell=True`.** Adding arguments to a shell string would let input like `; rm -rf ~` or `$(...)` run as commands. With a list, each item reaches the program as one literal argument.
- **Put `--` before the path.** Otherwise a path such as `-rf` or `--output=/etc/x` would be read as an option.
- **Restrict the extra arguments if users can set them.** Even without a shell, flags like `--exec` can be dangerous. If they come from users rather than trusted code, only accept flags from a fixed list.
- **Check the path where it enters the code.** That includes confirming it stays under an allowed base directory, if that applies here.
