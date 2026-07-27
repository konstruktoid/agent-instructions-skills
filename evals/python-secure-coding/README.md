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
