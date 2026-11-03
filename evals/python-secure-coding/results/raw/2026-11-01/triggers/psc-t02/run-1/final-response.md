I couldn't find the helper you mean. Nothing in this workspace builds a shell command: a search for `subprocess`, `os.system` and `shell` found nothing in any Python file. The only Python files are:

- `src/ledger/client.py`, a retry wrapper around a `transport` callable, with no shell use
- `src/ledger/balance.py`
- `tests/test_balance.py`

Can you paste the helper or tell me its file path? I also can't edit files or run `ruff`/`ty` in this session; I only have read and search access here. So once I see the helper, I'll send you the refactored code as a patch to apply.

Here's the shape I'd aim for, since passing a user-supplied path plus extra arguments is a common way to get shell injection:

```python
import subprocess
from collections.abc import Sequence
from pathlib import Path


def run_tool(path: str | Path, extra_args: Sequence[str] = ()) -> subprocess.CompletedProcess[str]:
    """Run `tool` on *path*, appending caller-supplied *extra_args* verbatim."""
    target = Path(path)
    cmd = ["tool", *extra_args, "--", str(target)]
    return subprocess.run(cmd, check=True, capture_output=True, text=True)  # noqa: S603 - argv list, no shell
```

- **Pass a list of arguments with no shell.** Don't use `shell=True`, `os.system` or f-string command lines. The path and each extra argument then reach the program as single, literal arguments, so characters like `;`, `$()` or spaces in a filename are never interpreted.
- **Put `--` before the path.** Otherwise a path like `-rf` or `--output=/etc/x` would be read as an option.
- **Decide how far to trust the extra arguments.** If they come from end users, not just from your own code, a list of arguments isn't enough. Some options are dangerous in themselves, like `--exec` or output-path flags. In that case, check them against an allowlist of permitted flags.
- **Check the path where it comes in, if needed.** For example, resolve it and confirm it stays inside an expected base directory.
