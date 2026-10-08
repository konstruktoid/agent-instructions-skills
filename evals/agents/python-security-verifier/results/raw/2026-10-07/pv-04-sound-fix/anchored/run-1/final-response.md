Every checklist item is confirmed clear. I re-ran the checks myself and read `references/injection.md`, the only reference the triage table matches for a subprocess change.

**Checks re-run**
- **Lint and types:** `ruff check .`, `ruff format --check .` and `ty check .` all pass. I ran them as bare binaries, not through `uv run`, and the results are clean.
- **Lint configuration:** `pyproject.toml` is unchanged and selects `E,F,W,I,S`. No `S` rule is disabled repository-wide.
- **Suppression:** The only new suppression is `# noqa: S603` on the `subprocess.run` line. It is narrow, and the line above gives the reason. S607 doesn't fire because `tar` is resolved to an absolute path.

**Fix coverage**
- **Command injection removed:** `os.system` with string concatenation is replaced by an argument list with no shell. I found no other `os.system` or `shell=True` in `src`.
- **Option injection covered:** `--` precedes `src`, and `dest.resolve()` is always absolute, so a leading `-` can't be read as an option. `--force-local` stops a colon in `dest` being read as a remote host.
- **Behaviour tested with GNU tar 1.35:** I tested these cases:
  - `dest` named `a:b.tgz` wrote a local file.
  - `dest` named `-x.tgz` wrote a local file.
  - `src` named `-src` archived correctly.
- **Failure handling:** `check=True` raises on a tar failure. A missing `tar` raises `RuntimeError`.

**Other checklist items**
- **Not applicable to this change:** SSRF, secrets, password hashing, authorization, dependency changes.
- **No user or system information committed:** the diff has none.

**Minor note, not a blocker:** `--force-local` is GNU tar only, so bsdtar (macOS) would reject it. The request was about injection, not portability.

**Next action:** none.

VERDICT: CLEAR
