This is a structural change only — no remote exists on this repo (`git remote -v` returned nothing), so the workflow cannot actually be run on a runner; that part of verification is not possible here and I'm reporting it as unverified.

## Summary

**Files changed:**
- `.github/workflows/pr-triage.yml` (new) — triage workflow, no checkout, no third-party actions.
- `README.md` — added a "Workflows" section documenting both workflows.

**Design:**
- Trigger: `pull_request_target`, `types: [opened]` — required because fork PRs get a read-only token under plain `pull_request`, which can't comment/label. No fork code is ever checked out or executed; only event metadata (`number`, `title`, `user.login`) is read.
- Permissions: `permissions: {}` at workflow level, `issues: write` at job level — verified against GitHub's own OpenAPI schema that the comment, label, and label-creation endpoints are all `issues.*`, not `pull-requests.*` (the skill's own quick-reference table says `pull-requests: write`; I overrode it with schema evidence — flagging that table as worth a correction).
- All steps use `gh` CLI with values passed via `env:`, never `${{ }}` interpolated into `run:`.

**Verify loop (1 attempt, converged):**
- `actionlint`: clean.
- `zizmor --persona=pedantic`: 3 low/high findings, all expected and accepted, not suppressed:
  - `dangerous-triggers` on `pull_request_target` — the deliberate exception this task requires; justified inline and here.
  - `undocumented-permissions` on `issues: write` — a comment is present on its own line, but zizmor's detector only credits a trailing same-line comment; your CLAUDE.md bans trailing comments except machine pragmas, so I kept the own-line comment and accepted this low-severity note rather than violate house style.
  - `concurrency-limits` on the pre-existing `ci.yml` — untouched by this change, not in scope.
- Workflow execution itself: **unverified** — no git remote is configured, so there's no way to push a branch or open a PR to exercise it on a runner.
