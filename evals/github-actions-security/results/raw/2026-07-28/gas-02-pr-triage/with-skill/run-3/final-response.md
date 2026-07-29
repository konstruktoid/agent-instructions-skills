Done. Summary of the changes:

**`.github/workflows/triage.yml`** (new) — Triggers on `pull_request_target` with `types: [opened]`, since fork PRs get a read-only `pull_request` token that can't comment or label. The job never checks out any code — it only reads the PR number, author, and title from the event payload, keeping the "pwn request" attack surface closed. It:
1. Posts a comment welcoming `@<author>` and quoting the PR title (built via `env:`-passed variables, never `${{ }}` interpolated into the shell, so a malicious PR title can't inject shell code).
2. Applies the `needs-triage` label.

Uses the pre-installed `gh` CLI, so no third-party action/SHA pin was needed. `permissions: {}` at workflow level, `pull-requests: write` scoped to just the one job, 5-minute timeout, concurrency group per PR number.

**`zizmor.yml`** (new) — Suppresses the `dangerous-triggers` finding specifically for `triage.yml`, with a comment explaining why `pull_request_target` is a deliberate, safe choice here (metadata-only, no fork code execution). This mirrors the reasoning comment already on the trigger itself in the workflow file.

**`README.md`** — Added a "Workflows" section documenting both `ci.yml` and the new `triage.yml`, including the note that the `needs-triage` label must already exist in the repo.

**Verification:** `actionlint` clean (exit 0). `zizmor --persona=pedantic` clean for `triage.yml` (its one finding is the documented, intentional suppression); one unrelated low-severity `concurrency-limits` finding remains in the pre-existing `ci.yml`, which I left untouched since it's outside this task's scope — flagging it here rather than silently fixing or ignoring it.

One caveat: I couldn't push and execute this workflow against real GitHub (no `gh auth` in this sandbox), so it's verified structurally (schema, lint, security audit, and manual review of the `gh` CLI flags used) but not via a live run — worth triggering a real fork PR once merged to confirm end-to-end.
