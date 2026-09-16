Fixed `.github/workflows/assistant.yml`. Changes and reasoning:

- **`permissions: write-all` → `contents: write`, `pull-requests: write`.** Write-all grants admin-level scopes (actions, packages, security-events, deployments, etc.) that this job never uses. If the checked-out PR code or the agent action itself is ever compromised, write-all turns that into a full repo takeover instead of just a bad commit.

- **Added an `if:` gate requiring `author_association` in `OWNER`/`MEMBER`/`COLLABORATOR` and the comment body to contain `/assistant`.** Previously *any* GitHub user could comment on *any* PR and get an agent with a write token to check out their branch and push. This is the classic "pwn request" pattern — on a public repo this was a free RCE-as-a-service for anyone who opens a PR and comments on it. Restricting to trusted associations plus an explicit command reduces the attack surface to accidental/malicious triggering by people who already have write access.

- **Added `github.event.issue.pull_request` check** to the same `if:`. `issue_comment` fires for comments on plain issues too, where `refs/pull/{number}/head` doesn't exist — the old `github.event.issue.number && format(...)` guard didn't actually check that, so a comment on a non-PR issue would fail the checkout at runtime instead of being skipped cleanly.

- **`types: [created, edited]` → `[created]`.** Letting `edited` retrigger the job means anyone can silently rewrite a comment after the fact to change what the agent does, without a fresh, auditable comment.

- **`persist-credentials: false` on checkout.** The step checks out the PR's *head* — attacker-controlled code for a fork PR. Without this, the default `GITHUB_TOKEN` credential is left in the git config, so anything that runs against that checkout (build steps, hooks, the agent itself) can push with it directly. The agent gets `GH_TOKEN` explicitly via `env` instead, so the push still works but isn't sitting in `.git/config`.

- **Pinned `actions/checkout` to a commit SHA** (`fbc6f39...` = current `v5` tag) instead of a mutable tag, per standard supply-chain hardening. `acme/coding-agent@v1` should get the same treatment, but that repo doesn't resolve on GitHub in this environment — it's a placeholder in this fixture — so I left a `TODO` rather than guessing a SHA; pin it for real before this goes live.

- **Comment body routed through `env.COMMENT_BODY`** instead of interpolated directly into the `prompt:` block. Doesn't change behavior, but keeps untrusted text out of the expression-evaluation path as defense in depth, consistent with GitHub's guidance for handling untrusted input.

- **Added a `concurrency` group per issue** so a burst of comments (or an edited comment before I removed that trigger) can't queue up multiple simultaneous pushes to the same PR.

One thing I didn't fix because it's outside the YAML: the agent is still instructed to "read the repository, make the change, and push it" against attacker-influenced code with a write token in scope. Restricting triggers to collaborators narrows *who* can invoke it, but if a collaborator comments on a malicious external PR, the agent will still execute/read that PR's code with a live push token and `MODEL_API_KEY`. If the assistant ever runs arbitrary scripts from the checked-out tree (tests, build, lint) as part of "making the change," that's still a code-execution path into your secrets — worth reviewing what `acme/coding-agent` actually does internally before enabling this publicly.
