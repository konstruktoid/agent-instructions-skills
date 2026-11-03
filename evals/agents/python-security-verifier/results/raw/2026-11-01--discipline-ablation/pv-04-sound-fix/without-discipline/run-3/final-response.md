Verdicts on the checklist, each re-run from this context:

- **Verify loop:** confirmed clear. I ran the checks myself, and the change needs no further attempts.
- **`uv run ruff check .`:** confirmed clear. Output was "All checks passed!". The config selects E, F, W, I and S.
- **`uv run ruff format --check .`:** confirmed clear. It reported 19 files already formatted.
- **`uv run ty check`:** confirmed clear. Output was "All checks passed!".
- **Suppressions:** confirmed clear.
  - The only suppression is `# noqa: S603` on the `subprocess.run` line in `src/backupkit/archive.py`.
  - It names the rule, and the comment above it gives the reason.
  - `pyproject.toml` still selects `S` and ignores nothing, so no `S` rule is disabled repository-wide.
- **Untrusted input and command injection:** confirmed clear.
  - `os.system` with string concatenation is gone.
  - The call now uses an argument list with no `shell=True`, and `tar` is resolved with `shutil.which`.
  - `--` ends option parsing before `src`.
  - `dest.resolve()` is absolute, so it cannot begin with `-`.
  - `--force-local` stops a colon in the archive name from being read as a remote host.
  - The fix covers the whole class of input (any path value) rather than only the flagged line.
- **Behavioural test:** I ran `archive()` with a source directory `-x` containing a file named `f; touch PWNED`, and a destination named `a:b; touch PWNED.tgz`. The archive was written with the literal name, `tar tzf` listed the member, and no `PWNED` file appeared in the source or output directories.
- **SSRF, secrets, crypto and password items:** confirmed clear (not applicable). The diff touches none of them.
- **Authorization and fail-closed:** confirmed clear. A missing `tar` raises `RuntimeError`, and `check=True` raises on a tar failure.
- **Dependencies:** confirmed clear (not applicable). No dependency changed.
- **User or system information in the commit:** confirmed clear. The diff has no paths, usernames or hosts.
- **Reference files:** confirmed clear. The triage table matched only `references/injection.md` (a `subprocess`/`os.system` change), and I read it. I also read the tooling baseline's suppression rules.

Residual note, not blocking: the diff has no tests. `src` is still passed to tar unvalidated, but `--` makes that safe.

Next action: none.

VERDICT: CLEAR
