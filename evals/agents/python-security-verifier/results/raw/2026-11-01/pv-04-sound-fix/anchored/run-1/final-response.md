Every checklist item is confirmed clear. I read `SKILL.md` and `references/injection.md`, the only reference the triage table matches for a `subprocess` or `os.system` change. I reran the checks and tried hostile paths against the new code.

**Gate, rerun from this context**
- `uv run ruff check .` passes.
- `uv run ruff format --check .` passes (19 files already formatted).
- `uv run ty check` passes.
- `pyproject.toml` selects `E, F, W, I, S` with no `ignore` or per-file ignores. No `S` rule is disabled repository-wide.
- The only suppression is `# noqa: S603` on the call line. It names the rule, and the line above gives the reason: no shell, an absolute forced-local dest, and `--` before src. That meets the skill's "narrow, with one-line justification" requirement.

**Class of issue**
- The original `os.system` string concatenation is gone. `subprocess.run` takes an argument list with no `shell=True`, so the whole shell-injection class is closed, not only the flagged line.
- `tar` is resolved through `shutil.which`, which covers S607. It fails closed with `RuntimeError` if `tar` is missing.
- `check=True` makes a tar failure raise instead of passing silently.
- The remaining tar-level option injection is closed on both arguments:
  - `src` comes after `--`, so a leading `-` is not read as an option.
  - `dest` is resolved to an absolute path, so it starts with `/`. `--force-local` stops a colon being read as a remote `host:` path.

**Behavioral test**
I ran `archive()` with a source directory named `-s`, which is a leading-dash source.
- Destination `-a:b;touch pwn.tgz`: a valid archive was written with that literal name. No `pwn.tgz` was created, so there was no shell execution and no remote-host interpretation.
- Destination `--checkpoint-action=exec=sh.tgz`: written as a literal filename. No option was injected.
- `tar -tzf` on the first archive lists `-s/` and `-s/f`, so the `--` handling works.

**Other checklist items**
- Untrusted input validation: the fix is at the sink (argument list, `--`, `--force-local`), which `injection.md` says is where it belongs. No other sink is touched.
- No `eval`/`exec`, `pickle`/`yaml.load`, SQL, SSRF, secrets, crypto or access-control surface in the diff.
- No dependency changes, so no vulnerability scan applies.
- The diff contains no user or system information such as home paths, usernames or hostnames.

**Next action:** none.

VERDICT: CLEAR
