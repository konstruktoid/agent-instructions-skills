`actionlint` is clean. `zizmor` has one remaining finding, which I could not fix and am reporting rather than suppressing.

## What was wrong

`.github/workflows/assistant.yml` had every risk this skill flags for a comment-triggered agent:

1. **`permissions: write-all`** — the job could rewrite any part of the repo, not just push a branch.
2. **Any commenter, not just maintainers, could trigger it.** `issue_comment` with no actor check runs on a comment from anyone, including a fork contributor on their own PR, with `write-all` and the model API key.
3. **`types: [created, edited]`** let an edited comment fire a second run.
4. **No distinction between an issue comment and a PR comment** — the checkout logic assumed the latter.
5. **Checkout used a mutable ref** (`refs/pull/N/head`) resolved at checkout time, not the commit the maintainer's comment actually corresponded to — a window for the fork owner to push new commits between comment and checkout.
6. **No `persist-credentials: false`** — the write-scoped token was left in `.git/config` for a step that also runs a model with a shell.
7. **The PR head is fork-authored code**, but nothing stopped the agent from reading a `CLAUDE.md`/`AGENTS.md`/`.mcp.json` planted in that PR, which can redirect the agent's own instructions or tool config.
8. **Unpinned actions** (`actions/checkout@v5`, `acme/coding-agent@v1`) — mutable tags.
9. **No `timeout-minutes`**, default 360 minutes.

## What changed

- `permissions: {}` at workflow level; the job now has only `contents: write` (to push) and `pull-requests: read` (to resolve the head SHA), each commented with why.
- `types: [created]` only, and the job's `if` requires `github.event.issue.pull_request != null` plus `author_association` in `OWNER`/`MEMBER`/`COLLABORATOR`.
- Added a step that resolves that association to an actual repo role via `gh api .../collaborators/{user}/permission` and aborts unless it's `write` or `admin` — `author_association` alone isn't a permission check (`COLLABORATOR` includes read-only invitees).
- Added a step that resolves the PR head to an immutable SHA via the API before checkout, and checks out that SHA instead of a branch ref.
- `actions/checkout` pinned to `3d3c42e5aac5ba805825da76410c181273ba90b1` (v7.0.1, current release), with `persist-credentials: false`.
- Added a step that deletes `CLAUDE.md`, `AGENTS.md`, `.mcp.json`, `.claude` from the checkout before the agent runs, since that checkout is fork-authored, not maintainer-authored.
- `timeout-minutes: 20`, and a `concurrency` group per PR (not cancel-in-progress, since cancelling mid-push leaves partial state).

## Unresolved — needs your input

`acme/coding-agent` doesn't resolve via the GitHub API (404) — it's a placeholder, so I can't pin it to a real SHA without fabricating one, which the skill explicitly forbids. Left a `TODO` comment on that line and it's zizmor's one remaining finding (`unpinned-uses`, high severity). Tell me the real action reference and I'll pin it and also check whether its `with:` inputs support a tool allowlist, which the agent-workflow guidance also calls for.

I did not touch `ci.yml`; zizmor also flagged two pre-existing, unrelated findings there (missing job name, missing workflow-level concurrency) that are outside this task.

**Files changed:** `.github/workflows/assistant.yml`
