I re-ran the checks and tested the fix with hostile paths. I found no unresolved items.

- **Gate:** I ran `uv run ruff check .`, `uv run ruff format --check .` and `uv run ty check` myself. All three pass.
- **Suppressions:** The only suppression is a call-site `# noqa: S603` on the `subprocess.run` line, with its reason on the line above. `pyproject.toml` still selects `S` and has no ignores, so no `S` rule is disabled repository-wide. `ty` has no new suppressions.
- **Class of issue:** The call is now `subprocess.run` on an argument list with no shell, so shell metacharacters in either path are not interpreted. `tar` is resolved with `shutil.which`.
- **Option injection:** `--` comes before `src`, so a source path starting with `-` is read as a file. `dest` is resolved to an absolute path, so it can't start with `-`. `--force-local` stops a `host:` prefix being read as a remote.
- **Behavior:** I called `archive()` with a source directory named `-x`, a destination named `-evil:a;touch pwn.tgz`, and a destination named `h:o.tgz`. Both archives were written literally to the local directory. No `pwn.tgz` appeared, and `tar -tzf` listed `-x/a` from the `h:o.tgz` archive.
- **References:** I read `references/injection.md`, the only file the triage table matches for subprocess and shell changes. Its rule is to pass argument lists instead of shell strings, and the change does that.
- **Unrelated checklist items:** The change touches no SSRF, secrets, crypto, access-control, dependency or user-information paths. I found nothing in the diff that bears on them.
- **Portability (not a security concern):** `--force-local` is a GNU tar option. BSD tar, the default on macOS, would reject it. That is a compatibility matter and doesn't change the verdict.

Next action: none.

VERDICT: CLEAR
