I re-ran the gate and tested the fix, and every checklist item holds.

**Gate, run from this context with `uv run`:**
- `uv run ruff check .` passed.
- `uv run ruff format --check .` passed (19 files already formatted).
- `uv run ty check` passed.
- `ruff` isn't on `PATH` in this environment, so I used `uv run`, as the skill requires.

**Checklist:**
- **Verify loop:** confirmed clear. All three checks pass on the first run.
- **Lint and type checks clean:** confirmed clear, as above.
- **Suppressions:** confirmed clear.
  - `pyproject.toml` is unchanged; the commit touches only `archive.py`, and `S` is still selected.
  - The only suppression is a call-site `# noqa: S603`, with a justification on the line above it.
  - The justification names the three controls: no shell, an absolute `--force-local` destination, and `--` before the source.
- **No untrusted data reaching a shell or `eval`:** confirmed clear.
  - `os.system` and its string concatenation are gone.
  - `subprocess.run` takes an argument list with no `shell=True`, so metacharacters in a path are never interpreted.
  - The executable is resolved with `shutil.which`, so `S607` doesn't apply.
- **Class of issue, not just the flagged line:** confirmed clear.
  - A source path starting with `-` can't be read as an option, because `--` precedes it.
  - A destination starting with `-` or containing `:` can't be read as an option or a remote host. It is resolved to an absolute path and `--force-local` is set.
  - I tested a source named `-v` with an archive named `-x.tgz`, and a source with `;` in a file name with an archive named `a:b.tgz`. Both archives were created, and no injected file appeared.
- **Input validation at the boundary:** confirmed clear. The function takes typed `Path` values and handles them safely at the sink, which the reference file treats as a separate control from validation.
- **Not applicable:** confirmed clear for the SSRF, secrets, password and randomness, access-control and dependency items. The change has no network calls, credentials, auth logic or dependency changes (`dependencies = []`).
- **No user or system information committed:** confirmed clear. The diff has no paths, hostnames or usernames.
- **Reference files read:** confirmed clear. The triage table matches this change (`os.system`, `subprocess`, shell strings) only to `references/injection.md`, and I read it.

**Non-blocking observation:** `--force-local` is a GNU tar option. On a BSD `tar` the call would fail with an error, not become unsafe. That is portability, not security.

**Next action:** none.

VERDICT: CLEAR
