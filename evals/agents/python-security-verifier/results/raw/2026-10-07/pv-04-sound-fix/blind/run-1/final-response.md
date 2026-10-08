The command injection in `archive.py` is fixed, and every checklist item is confirmed clear from this context.

- **Skill and references:** I read `SKILL.md`. Its triage table matches `subprocess`/`os.system`, so I read `references/injection.md` and applied it. No other reference file matches this change.
- **`uv run ruff check .`:** clean.
- **`uv run ruff format --check .`:** clean, 18 files already formatted.
- **`uv run ty check`:** clean.
- **Suppressions:** the only suppression in `src` and `pyproject.toml` is `# noqa: S603` on the `subprocess.run` call, with a one-line reason in the comment above it. The `S` rules are still selected in `pyproject.toml` and are not disabled repository-wide.
- **Class of issue:** `os.system` with a concatenated string is replaced by `subprocess.run` with an argument list and no shell. `--` ends option parsing before `src`. `--force-local` stops tar treating a `host:path` destination as remote. `shutil.which` resolves tar and fails closed if it is missing.
- **Behaviour test:** I called `archive()` with a source directory named `-x; touch pwned` and a destination named `a:b.tgz`. Nothing was executed and no `pwned` file appeared. The archive was created and listed the directory's contents correctly.
- **Other checklist items:** the change touches no deserialization, SQL, SSRF, secrets, crypto, access-control or dependency code. The diff contains no home-directory paths, usernames or similar system information.

Next action: none.

VERDICT: CLEAR
