I checked the fix by re-running the gate and by feeding the function hostile paths. Every checklist item is confirmed clear.

**Gate, re-run in this context**
- `uv run ruff check .` passed ("All checks passed!").
- `uv run ruff format --check .` passed.
- `uv run ty check` passed.
- The ruff config selects `E, F, W, I, S`, and `pyproject.toml` is unchanged. No `S` rule was disabled repository-wide.
- The only suppression is `# noqa: S603` on the `subprocess.run` line. It names the specific rule, and the comment above it gives a reason: no shell, a forced-local absolute `dest`, and `--` before `src`.

**Reference file**
- The triage table matched only `references/injection.md`, because the change touches `subprocess` and `os.system`. I read it. It requires argument lists instead of shell strings, and the change does that.

**Behavior test**
- I ran `archive()` on a directory named `a; touch PWNED` with a destination named `o: 1$(id).tgz`. No `PWNED` file was created, and no command substitution ran. The archive was written under its literal name.
- I ran it on a source directory named `-x` and a destination named `-o.tgz`. Both were treated as plain paths, not options. The archive listing was correct.
- `--force-local` stops tar reading a `:` in the destination as a remote host. `dest.resolve()` makes the destination absolute. `--` stops option parsing before `src`.

**Class of issue, not just the flagged line**
- `os.system` string concatenation is gone, and no `shell=True` remains.
- Both path arguments are now handled safely, not just one.
- `check=True` makes a tar failure raise instead of passing silently.
- A missing `tar` raises `RuntimeError`, so the code fails closed.

**Other checklist items**
- None of these apply to this change: SSRF, secrets, crypto and password hashing, authorization, dependencies, and user or system information. No home paths, usernames or hostnames were added, and I found no concerns.

**Non-blocking note:** `--force-local` is a GNU tar option. On a BSD tar, such as the one on macOS, the call would fail with an error. That is a portability limit, not a security flaw, and it fails closed.

**Next action:** none.

VERDICT: CLEAR
