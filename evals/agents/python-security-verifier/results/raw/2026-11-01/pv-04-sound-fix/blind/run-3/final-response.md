All checklist items are confirmed clear. I reran the checks from this context and found no counterexample to the fix.

**Gate (rerun with `uv run`)**
- **`ruff check .`:** clear ("All checks passed!"). The repo selects `E, F, W, I, S`, so the `S` rules are active.
- **`ruff format --check .`:** clear (19 files already formatted).
- **`ty check`:** clear.
- **Suppressions:** the only new one is `# noqa: S603` on the single `subprocess.run` call. It names the specific rule and the line above gives a reason. No `S` rule is disabled repository-wide, and `pyproject.toml` is unchanged by the commit.

**Reference read:** I read `references/injection.md`, the only file the triage table matches for `os.system` and `subprocess`.

**Class of issue, not just the flagged line**
- **No shell:** `os.system` and string concatenation are replaced with an argument list and no `shell=True`. Shell metacharacters in `src` or `dest` are never interpreted.
- **Option injection:** `--` precedes `src`, so a `src` such as `-rf` or `--to-command=...` is treated as a member name. `dest.resolve()` is absolute, so it cannot begin with `-`.
- **Remote-archive syntax:** `--force-local` stops a `host:path` style `dest` being read as a remote archive.
- **Binary lookup:** `tar` is resolved with `shutil.which`, and the code fails closed with a `RuntimeError` if it is missing.
- **Dynamic test:** I ran `archive()` on a directory named `a b;touch PWNED` with a destination named `x:y.tgz`. The archive was created with the right contents and no `PWNED` file appeared.

**Other checklist items:**
- **Remaining injection items:** none apply or fail. The change has no eval, deserialization, SQL, SSRF, secrets, crypto or access-control surface, and no dependencies changed.
- **System information:** the diff contains no usernames, paths or hostnames.

**Non-blocking note:** `--force-local` is a GNU tar option, so the function would fail on bsdtar. This is a portability point rather than a security one.

**Next action:** none.

VERDICT: CLEAR
