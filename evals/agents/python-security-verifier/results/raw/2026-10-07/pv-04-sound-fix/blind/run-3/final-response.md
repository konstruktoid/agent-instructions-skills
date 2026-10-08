Both archives were created, no `PWNED` file appeared, and the metacharacter and leading-dash destinations were treated as plain filenames. (The tar listing error came from my own `--` in the check command, not from the fix.)

**Checklist verdicts**
- **Verify loop:** confirmed clear. I ran every check myself, and each was clean on the first run.
- **`uv run ruff check .`:** confirmed clear ("All checks passed!").
- **`uv run ruff format --check .`:** confirmed clear (18 files already formatted).
- **`uv run ty check`:** confirmed clear ("All checks passed!").
- **Suppressions:** confirmed clear. The only suppression is a call-site `# noqa: S603` in `archive.py`, with a one-line justification above it. `pyproject.toml` selects `S` and disables nothing.
- **Untrusted input and the class of injection:** confirmed clear. `os.system` with string concatenation became `subprocess.run` with an argument list and no shell, so shell injection through either path is gone. The remaining tar-option injection is closed too: `dest` is resolved to an absolute path, which stops a leading `-`, and `--` precedes `src`. `--force-local` stops a `host:` prefix in `dest` from being read as a remote. `check=True` surfaces failures. `shutil.which` raises a clear error when tar is missing.
- **SSRF, secrets, crypto, access control and dependencies:** confirmed clear because they are not applicable. The diff touches none of them and changes no dependencies.
- **Nothing committed carries user or system information:** confirmed clear. The diff has no paths, usernames or hostnames.
- **Reference files:** confirmed clear. The triage table matched only `references/injection.md` (subprocess and `os.system`), and I read and applied it.

No concerns remain. Next action: none.

VERDICT: CLEAR
