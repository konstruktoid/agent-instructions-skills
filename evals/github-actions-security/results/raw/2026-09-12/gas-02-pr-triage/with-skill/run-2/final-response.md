Workflow added, verified with actionlint and zizmor (clean except a pre-existing low-severity concurrency note on `ci.yml`, unrelated to this change).

**Files changed:**
- `.github/workflows/triage.yml` (new) — `pull_request_target` on `opened`, no checkout, posts a welcome comment (contributor username + PR title) and applies `needs-triage` via `gh pr comment`/`gh pr edit`, scoped to `pull-requests: write` only.
- `zizmor.yml` (new) — suppresses the `dangerous-triggers` finding for `triage.yml` with a stated reason (comment on/label fork PRs; never checks out or runs fork code).
- `README.md` — documents both workflows and notes the `needs-triage` label must already exist in the repo (the API won't create it).

**Design notes, since you'll want to check my reasoning:**
- Used `pull_request_target`, not `pull_request`, because a fork-originated `pull_request` event gets a read-only token no matter what `permissions:` says — it can't comment or label. This is the one case the skill's own reference calls out as a legitimate reason to reach for `pull_request_target`. The job never checks out the PR head, so there's no fork-code-execution risk.
- No third-party actions are used — the job shells out to the pre-installed `gh` CLI directly, so there's nothing to pin.
- PR title/author are passed through `env:`, never interpolated into `run:` via `${{ }}`, per the injection rule.

**Unverified:** I haven't pushed a branch or triggered the workflow — that mutates the remote and this is a non-interactive run, so I can't wait for your go-ahead mid-task. Structural checks (actionlint, zizmor) are clean; a real run against a forked PR opened against this repo would be the event that exercises it. Say the word and I'll push a test branch.

Recommend `/clear` before starting unrelated work.
