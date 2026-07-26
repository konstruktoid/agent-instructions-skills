# python-secure-coding evals

Five feature requests, each against a fixture carrying a planted flaw that the skill's
OWASP-aligned checklist covers on the code path the request forces the agent to touch:
`shell=True` on a concatenated command, `pickle.loads` and `eval` on client input, SQL built
by concatenation, an SSRF plus a hardcoded token and `random`-derived identifiers, and md5
password hashing with a `==` token comparison. No prompt mentions security, so only the skill
can surface them. Every fixture ships a thin ruff configuration rather than `select = ["ALL"]`,
which keeps flake8-bandit out of the picture and means a pass measures the skill instead of
the linter. Run it with `python3 evals/run_eval.py tasks --skill python-secure-coding`, then
`report` to regenerate `results/<date>.md`. Read the delta column first: zero means the
baseline already handled that task and the fixture needs a harder flaw, not that the skill
succeeded.
