Both checks pass on `assistant.yml`: actionlint clean, zizmor clean offline. One attempt, no oscillation. Full online zizmor coverage isn't possible because `acme/coding-agent` doesn't resolve on GitHub — see the flag below.

## What was wrong

The original workflow let any commenter on any issue trigger an agent that held `write-all` and a model API key, with no way to know in advance what it would do:

- **`permissions: write-all`** — every scope, at workflow level, so any job (and the agent process itself) held it.
- **No actor gate at all.** `issue_comment` fires for any commenter, including on issues, not just PRs, so anyone (a public repo means anyone with a GitHub account) could get the agent to run with full write access and the model credential.
- **Unpinned actions** — `actions/checkout@v5` and `acme/coding-agent@v1` are mutable tags, not commit SHAs.
- **`persist-credentials` left at its default** on checkout, so the token sat in `.git/config` where the agent's own read access could find it, in addition to it being handed to the agent step directly via `GH_TOKEN`.
- **The agent process held the push-capable token and the model key simultaneously**, with no separation between "the agent edits files" and "something pushes."
- **`types: [created, edited]`** let an edited comment re-trigger the same run.
- Comment body was spliced into the prompt with no framing distinguishing it as untrusted task text from instructions — not fixable by escaping, but worth stating explicitly.

## What I changed

- `permissions: {}` at workflow level; job gets only `contents: write` and `pull-requests: read`, each commented with why.
- Two-layer actor gate: a job-level `if` on `author_association` (cheap, blocks obviously unauthorized runs before checkout), followed by a real `collaborators/.../permission` API check requiring `role_name` of `write` or `admin` — the association check alone isn't a permission check (`COLLABORATOR` includes read/triage invitees).
- Trigger narrowed to `types: [created]`, gated on `github.event.issue.pull_request != null` so issue comments can't fire it.
- PR head resolved via the API to an immutable SHA (and its ref/repo), not a mutable branch pointer, and that SHA is what's checked out.
- `actions/checkout` pinned to `3d3c42e5aac5ba805825da76410c181273ba90b1` (v7.0.1, current release), `persist-credentials: false`.
- `CLAUDE.md`/`AGENTS.md`/`.mcp.json`/`.claude` stripped from the checkout before the agent runs, so a fork can't plant its own agent instructions in the PR it's asking about.
- The agent step no longer receives any GitHub token — it gets `MODEL_API_KEY` and the comment body only. Commit and push happen in a separate, deterministic step afterward, using `GITHUB_TOKEN` injected only into that step's environment (not persisted to disk), and only if the PR head is in the same repo (a fork's branch can't be pushed to with this token regardless).
- `concurrency` keyed on the PR number, `timeout-minutes: 20`.

**Unresolved, needs your input:** `acme/coding-agent` doesn't exist on GitHub under that name (404), so I pinned it to a placeholder all-zero SHA with a `TODO` comment — you must replace `acme/coding-agent` with the real owner/repo and resolve its actual release SHA before merging. This also means zizmor's online supply-chain checks (`impostor-commit`, `stale-action-refs`, etc.) couldn't run for that reference; I verified with `--offline` instead, which is clean, but you should rerun zizmor with `GH_TOKEN` set once the real action reference is in place.

Files changed: `.github/workflows/assistant.yml`.
