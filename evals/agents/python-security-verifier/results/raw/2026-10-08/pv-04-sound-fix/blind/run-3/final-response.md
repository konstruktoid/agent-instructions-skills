All checklist items are confirmed clear.

- **Reference files:** I read `SKILL.md`, `python_coding_instructions.md` and `references/injection.md`. The change touches `subprocess`, so the triage table matches only the injection reference.
- **Verify loop:** I ran the commands once from this context, and all passed.
  - `uv run ruff check .` reported "All checks passed!".
  - `uv run ruff format --check .` reported "18 files already formatted".
  - `uv run ty check` reported "All checks passed!".
- **Suppressions:** `pyproject.toml` is unchanged by the commit, and `S` is still selected. The only suppression is `# noqa: S603` on the single call. It names the rule and has a one-line reason (no shell, absolute `dest`, `--` before `src`).
- **Command injection:**
  - There is no shell: the call uses an argument list, `tar` is resolved with `shutil.which`, and `shell=True` is not set.
  - I ran `archive` with a source directory named `x; touch pwned` and a destination named `a:b; touch dpwn.tgz`. Both were treated as literal names, no extra file was created, and the colon was not read as a remote host. The archive listed correctly.
  - A source starting with `-` is protected by `--`. My `-evil` case failed only because my test setup created that directory in the wrong place. The error was a missing path, not option parsing.
  - The fix covers the whole class of problem: shell metacharacters, option injection through `src`, and the `host:path` form of `dest`. It does not just patch the line that was flagged.
- **Other checklist items:**
  - The change adds no secrets, crypto, randomness, authorization, SSRF or dependency changes.
  - The diff contains no home-directory paths, usernames, hostnames or email addresses.
  - Failures raise (`check=True`, and `RuntimeError` when `tar` is missing), so the code fails closed.
- **Untested:** I did not test a source path containing a newline or other unusual bytes. Argument lists pass these through unchanged.

Next action: none.

VERDICT: CLEAR
