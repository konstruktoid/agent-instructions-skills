# python-secure-coding evals

Five feature requests, each against a fixture carrying a planted flaw that the skill's
OWASP-aligned checklist covers on the code path the request forces the agent to touch:
`shell=True` on a concatenated command, `pickle.loads` and `eval` on client input, SQL built
by concatenation, an SSRF plus a hardcoded token and `random`-derived identifiers, and a fast
hash over passwords with a token comparison that is not constant time. No prompt mentions
security, so only the skill
can surface them. Every fixture ships a thin ruff configuration rather than `select = ["ALL"]`,
which keeps flake8-bandit out of the picture and means a pass measures the skill instead of
the linter. Run it with `python3 evals/run_eval.py tasks --skill python-secure-coding`, then
`report` to regenerate `results/<date>.md`. Read the delta column first: zero means the
baseline already handled that task and the fixture needs a harder flaw, not that the skill
succeeded.

## Fixtures hardened on 2026-07-27

`psc-01`, `psc-03`, and `psc-05` scored full marks in both arms on 2026-07-25, which measures
task difficulty rather than skill effect. All three were rewritten so the flaw is a
plausible-looking helper the code already imports and calls, rather than a pattern a grep
would find:

- `psc-01`: `reportkit.shellutils` offers `quote_for_shell`, which wraps a path in double
  quotes and reads as sanitization while leaving `$(...)` live under `shell=True`, and
  `temp_output_path`, which builds a predictable path in the shared temp directory instead of
  creating the file atomically.
- `psc-03`: `auditlog.filters` offers `quote_literal`, which doubles embedded quotes correctly
  and so looks defensible, and `order_clause`, which interpolates a caller-supplied column and
  direction where no bound parameter is possible.
- `psc-05`: `accounts.crypto` hashes passwords with a salted, peppered SHA-256 rather than
  MD5, and `tokens_match` hashes both sides before comparing them with `==`, which equalises
  length without making the comparison constant time. The token is `secrets.token_urlsafe(6)`,
  so it uses the right module with too few bytes, and only its first four characters are
  logged.

The results files under `results/` predate this change. Every number in `results/2026-07-25.md`
was measured against the previous fixtures and is not comparable to anything measured after
this date.

## Fixtures anchored for `ty` on 2026-08-17

Every fixture now carries a `[tool.ty.environment]` section. `ty` resolves a project by walking
up for the nearest `pyproject.toml` that carries a `[tool.ty]` section, and a graded workspace is
a copy of a fixture nested under `results/raw/`, inside this repository. With no such section in
the fixture, `ty` settled on the repository's own `[tool.ty.src]` block and checked the copy
against the repository root as first-party code, and against the repository's `requires-python`
rather than the fixture's. `[tool.ruff]` already anchored ruff the same way, which is why only
the `ty-clean` assertion was affected. `root` also states the src layout, so a test file a run
adds can import the package under test.

Three `ty-clean` failures in `results/2026-07-28.md` came out of that resolution, all of them in
the with-skill arm, which absorbed them because it wrote the most code:

- `psc-03` run 3: the package under test was unresolvable from a test file the run added.
- `psc-05` run 1: `datetime.UTC` was reported as missing, because this repository declared
  `requires-python = ">=3.9"` on the date of the run while the fixture declares `">=3.11"`.
- `psc-04` run 2: the same unresolvable import, alongside two argument-type errors in the run's
  own test file that are real. That run still fails `ty-clean` after the anchoring, on those two.

The failure was one-directional. A planted type error inside a workspace under the repository's
exclude paths is still reported, because an explicitly passed path overrides an exclude, so the
anchoring removes false failures without turning any recorded pass into a failure. Correcting
the two false failures moves no median either, so the net delta of +4 stands; what the
resolution distorted is the observed range of the with-skill arm, which reads wider than the
runs warrant.

`results/2026-07-28.md` is therefore marked for regeneration. Its `ty-clean` column is not
reproducible against the current fixtures, and `regrade` cannot repair it, because the graded
workspaces are gitignored and no longer on disk. The stamp needs a fresh `tasks` run followed by
`report`.
