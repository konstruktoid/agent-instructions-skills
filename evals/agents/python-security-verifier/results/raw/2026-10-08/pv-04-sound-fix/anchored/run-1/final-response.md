I re-ran the checks myself and found no unresolved items.

**Checks I ran (via `uv run`)**
- `ruff check .` passed.
- `ruff format --check .` passed (18 files already formatted).
- `ty check` passed.

**Reference file:** the change touches `os.system`/`subprocess`, so the triage table routes it to `references/injection.md`. I read it and applied it.

**Checklist**
- **Lint and type gate:** confirmed clear. All three commands ran clean from this context.
- **Suppressions:** confirmed clear.
  - `pyproject.toml` selects `S` and has no `ignore` entry, so no `S` rule is disabled repository-wide.
  - The only new suppression is `# noqa: S603` on the call line. It names the rule, and the line above gives the reason.
- **No shell and no untrusted data reaching a shell:** confirmed clear. `os.system` with string concatenation is gone, and `subprocess.run` takes an argument list with no `shell=True`. `tar` is resolved with `shutil.which` and fails closed with a `RuntimeError` if it is missing.
- **Class of issue, not just the flagged line:** confirmed clear. Beyond the shell, the fix also closes option injection into `tar`.
  - I ran a hostile case against the real function.
  - The source directory was named `-x;touch PWNED`.
  - The destination was `--checkpoint-action=exec=id:o.tgz`.
  - No `PWNED` file was created and no command ran.
  - The archive was written at the literal name and contains the expected `-x;touch PWNED/f`.
  - This used GNU tar 1.35.
- **Other checklist items:** confirmed clear. The change involves no SSRF, secrets, crypto, auth or deserialization, and the diff contains no user or system information. No dependencies changed.
- **Reference file read and applied:** confirmed clear.

**Non-blocking note:** `--force-local` is a GNU tar option. bsdtar, for example on macOS, would reject it, so the function would fail there. That is a portability limit, not a security flaw, and it fails closed. Because `dest.resolve()` already produces an absolute path, the flag adds little.

Next action: none.

VERDICT: CLEAR
