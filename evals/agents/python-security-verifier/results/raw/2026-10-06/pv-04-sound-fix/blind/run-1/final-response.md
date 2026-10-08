The fix removes the command injection. Every checklist item is confirmed clear, and I re-ran each check myself.

**Tool gate (re-run from this context)**
- `ruff check .` passed.
- `ruff format --check .` passed (18 files already formatted).
- `ty check .` passed. I ran the bare binaries, not `uv run`, so these are not pinned-version runs.
- The repository enables `E`, `F`, `W`, `I` and `S` in `pyproject.toml`. No `S` rule is disabled repository-wide.
- The only suppression is `# noqa: S603` at the call site. It names the specific finding and gives a one-line reason in the comment above it.
- `S607` does not fire, because the executable is resolved to an absolute path with `shutil.which`.

**Class of issue, not only the flagged line**
- `os.system` with string concatenation is replaced by `subprocess.run` with an argument list and no `shell=True`. This is the fix `injection.md` prescribes.
- `--` ends option parsing before `src`, so a source path starting with `-` cannot be read as a tar option.
- `--force-local` stops tar treating a `host:path` destination as a remote target.
- `dest.resolve()` gives an absolute destination path.
- `check=True` makes a failed `tar` raise instead of passing silently.
- A missing `tar` raises `RuntimeError`. That is the safe outcome.

**Functional test**
- I called `archive()` with `src` set to `-x; touch pwned` and `dest` set to `o:a; touch pwned2.tgz`.
- The call produced the archive and no `pwned` or `pwned2` files appeared.
- My follow-up `tar tzf` on that archive failed because it read the `o:` in the filename as a remote host. That was my listing command, not the fixed code.

**Other checklist items**
- **Untrusted input and shell:** none reaches `shell=True`, `eval`/`exec`, `pickle`/`yaml.load` or SQL. The change has no deserialization, SQL or query code.
- **Not applicable:** the change has no SSRF, secrets, crypto or authorization code, and adds no dependencies.
- **System information:** the diff contains no home-directory paths, usernames or similar.
- **References:** the triage table matched only `injection.md` for this change, and I read it.

**Next action:** none.

VERDICT: CLEAR
