The command injection is fixed. I found no unresolved items.

- **Checks:** I ran `uv run ruff check .`, `uv run ruff format --check .` and `uv run ty check` from this context. All three passed.
- **Suppressions:** The only suppression is a call-site `# noqa: S603` on `subprocess.run`, with a one-line reason in the comment above it. `pyproject.toml` still selects `S` and has no ignores.
- **Skill checklist:** `references/injection.md` was the only reference the triage table matched (a subprocess change). No dependencies changed, so the vulnerability-scanner item doesn't apply. The diff adds no secrets, user data or access-control logic.
- **Fix covers the whole input class:** `os.system` with string concatenation is replaced by an argument list passed to `subprocess.run`, with no shell. That removes the injection through both `src` and `dest`, not only one line.
- **Option and remote-spec injection:** `--` comes before `src`. `--force-local` and `dest.resolve()` stop a `dest` that starts with `-` or contains `:` from being read as an option or a remote host.
- **Behavioural test:** I made a source directory named `a;touch PWNED` and another named `-x`. I archived both, with destinations `o:1.tgz;x.tgz` and `-o.tgz`. No shell ran: no `PWNED` file appeared. Both archives were created and listed the expected contents.
- **Residual note, not a failure:** `--force-local` is a GNU tar flag, so a non-GNU `tar` would fail with a non-zero exit. That fails closed and is a portability issue only.

Next action: none.

VERDICT: CLEAR
