Done. Files changed:

- `.github/workflows/pr-triage.yml` (new) — `pull_request_target`, `types: [opened]`; comments a welcome that names the contributor and repeats the PR title, then applies `needs-triage` (creating it first if missing). No checkout, so no fork code executes.
- `zizmor.yml` (new) — suppresses the `dangerous-triggers` finding for this file, with the reason documented inline.
- `README.md` — documents both workflows.

Design note I'm dropping deliberately: `pull_request` was rejected because fork PRs get a read-only `GITHUB_TOKEN`, which can't comment or label — that's the reason for `pull_request_target` here, stated in a comment on the trigger. All event data (`PR_AUTHOR`, `PR_TITLE`) goes through `env:`/`process.env`, never interpolated into script text.

Verify loop, attempt 2 (progress from attempt 1, then clean on the files I touched):
- `actionlint`: clean.
- `zizmor --persona=pedantic`: clean on `pr-triage.yml`. One pre-existing `low`-severity `concurrency-limits` finding remains on `ci.yml`, which I did not touch and is out of scope for this task — flagging it rather than fixing it silently.
- Not run: the workflow itself against a live event. Exercising it needs a real pull request (ideally one opened from a fork) against a pushed branch, which means `git push` — a state-changing action I won't take without you asking for it in this turn. So the change is structurally verified only; behavior is unconfirmed until such a PR runs it.
