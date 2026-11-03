I couldn't find that helper, so I haven't changed any code. The workspace has three Python files: `src/ledger/balance.py`, `src/ledger/client.py` and `tests/test_balance.py`. None of them calls `subprocess`, `os.system`, `Popen` or builds a shell string. `client.py:6` does have a `get(transport, path)` function that takes a path, but it only passes it to a transport callable and never makes a shell command.

Could you paste the helper or tell me which file it's in? It may not be committed yet, or it may be in another repo.

When I have it, here's how I'd refactor it, since the path comes from the user:

```python
import subprocess
from collections.abc import Sequence
from pathlib import Path

def run_tool(path: str | Path, extra_args: Sequence[str] = ()) -> subprocess.CompletedProcess[str]:
    """Run `tool` on *path*, appending caller-supplied *extra_args*."""
    resolved = Path(path).resolve(strict=True)  # validate at the boundary
    argv = ["tool", *extra_args, "--", str(resolved)]
    return subprocess.run(argv, check=True, capture_output=True, text=True)  # noqa: S603 - argv list, no shell
```

- **A list of arguments, not a shell string:** I'd drop `shell=True` and any string building. If the helper builds a string today, a path or extra argument containing `;`, `$()` or backticks could inject commands. With a list, each value reaches the program as one literal argument.
- **`--` before the path:** this stops a path starting with `-` from being read as an option.
- **Extra arguments as a sequence of strings:** they're passed through as separate items, never joined into a string. If any of them can come from a user rather than your own code, they should be checked against an allowlist of permitted flags.
- **Checking the path:** it's resolved and has to exist. It could also be restricted to an allowed base directory if that suits your case.

After the change I'll run `uv run ruff check .`, `uv run ruff format --check .` and `uv run ty check`.
