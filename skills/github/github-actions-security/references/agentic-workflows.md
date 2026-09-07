# Workflows That Run an Agent

Read this when a job invokes an AI coding agent, whether through a published action, a container
image, or a CLI installed in a step, and when a workflow is triggered by a comment addressed to one.

## Contents

- What changes when a job runs an agent
- Trigger and authorization
- Token scope and identity
- Constraining what the agent can run
- Configuration that arrives with the checkout
- Untrusted text reaching the model
- Reviewing what the agent produced
- Loops and cost
- Checklist

## What changes when a job runs an agent

An ordinary job runs the steps written in the workflow file. A job that runs an agent runs steps
chosen at execution time from text the job read, so the command set is not known at review time.
Every control that depends on reading the workflow to learn what it does stops holding: the diff
shows a step that invokes a model, and not the commands that step will decide to run.

What still holds is the set of controls the agent cannot lift from inside the job. Two of them
are in the table in [scalability.md](scalability.md), and two are not:

- The `permissions` block, which fixes the token's scopes for the life of the job.
- An `environment` with required reviewers, which gates the job behind a person and withholds that
  environment's secrets until the approval, described in
  [permissions-and-secrets.md](permissions-and-secrets.md).
- The rulesets on the branches and tags the token could otherwise write to.
- Egress restriction, with the caveat below, covered in [runners.md](runners.md).

Egress is the weakest of the four, because where it is applied matters. A restriction enforced at
the network layer around a self-hosted runner is outside the job. The in-job hardening action in
[runners.md](runners.md) is not: on a hosted runner the job has passwordless `sudo`, so that action
is defense in depth rather than a boundary, and it is worth setting its
`disable-sudo-and-containers` input.

A rule written into the agent's prompt is in none of these categories, because the prompt is the
surface being attacked.

## Trigger and authorization

Comment-driven and `pull_request_target` triggers carry every risk in
[untrusted-input.md](untrusted-input.md), and one more: the attacker-supplied text is not only
interpolated into a script, it is read as the instruction to follow.

- Gate on the actor before the agent step runs, in a job-level `if`, not in the prompt:

  ```yaml
  jobs:
    agent:
      if: >-
        github.event.comment.author_association == 'OWNER' ||
        github.event.comment.author_association == 'MEMBER' ||
        github.event.comment.author_association == 'COLLABORATOR'
  ```

- Treat that gate as necessary and not sufficient. `author_association` is not a permission check:
  `COLLABORATOR` covers anyone invited to the repository, read and triage access included, and
  `MEMBER` means membership of the owning organization, which implies nothing about this
  repository. Where the job holds a write token and a model credential, resolve the actual
  permission with `gh api repos/OWNER/REPO/collaborators/USER/permission --jq .role_name` and
  require `write` or `admin`. That call needs a token with push access, so the gate job carries
  `contents: write` or a separate installation token, which is a real cost to weigh against the
  gate it buys. Read `role_name` rather than `permission`, since a custom role collapses to
  `write` in the latter.
- Scope the trigger as narrowly as the event allows. `issue_comment` with `types: [created]` keeps
  an edited comment from firing a second run, and `github.event.issue.pull_request` is what
  distinguishes a pull request comment from an issue comment.
- A label applied by a maintainer is a stronger start signal than a comment, because applying it
  already requires write access. The pull request it fires on still carries a title and a body the
  fork wrote, so the gain is in who starts the run rather than in what the run then reads. A fork
  `pull_request` run gets a read-only token and no secrets, so the workable shape is
  `pull_request_target` on `types: [labeled]` with no checkout of fork code, or the two-workflow
  split in [untrusted-input.md](untrusted-input.md).
- The unconditional rule in [untrusted-input.md](untrusted-input.md) stands: do not check out the
  pull request head in a `pull_request_target` job. An agent step compounds it, because the fork's
  files can address the agent directly.
- Where fork code is checked out under a maintainer-authorized flow, resolve the head to a commit
  SHA and check that out, so the code the agent reads is the code the maintainer authorized rather
  than whatever the branch points at when the job starts.

## Token scope and identity

- The model provider credential is the secret this workflow always holds, and the one worth the
  most. Give it to the single step that needs it rather than the job, keep it in an environment
  gated by required reviewers where the repository accepts untrusted triggers, and never expose it
  to a step that runs repository-supplied code.
- Keep the workflow default at `permissions: {}` and grant scopes on the single job that needs
  them. An agent that only reads and comments needs `contents: read` and `pull-requests: write`.
- Never pass `secrets: inherit` to a reusable workflow that runs an agent. The agent decides what
  to run, so every secret in the environment is reachable by whatever it decides.
- Treat `pull-requests: write` and `issues: write` as outbound channels. An egress allowlist has to
  permit `api.github.com`, so those scopes let an instruction-injected agent publish whatever it
  read, over an allowed endpoint. What bounds them is that the write is small, public, and
  auditable, not the network policy.
- Never grant `id-token: write`. An agent with any shell reads `ACTIONS_ID_TOKEN_REQUEST_URL` and
  `ACTIONS_ID_TOKEN_REQUEST_TOKEN` from the job environment and mints an OIDC token itself, which
  is every cloud role whose trust policy matches this workflow. Never grant `actions: write`
  either: it re-dispatches workflows, which is the loop exception below, and it deletes artifacts
  and re-runs jobs.
- Do not grant an identity that can push to a protected branch. The agent opens a pull request and
  a person approves it, which is the separation of duties the ruleset already enforces for people.
- `GITHUB_TOKEN` cannot create or update files under `.github/workflows/`: there is no such scope
  in the `permissions` schema and the push is refused. The exposure is elsewhere, in granting the
  agent's GitHub App the Workflows permission or handing it a personal access token carrying the
  `workflow` scope. Read what an installation holds from Settings, GitHub Apps, on the
  installation's own page; the repository installation endpoint answers only to a JWT signed by
  the app, not to a user token.
- Where a token wider than `GITHUB_TOKEN` is needed, mint a short-lived GitHub App installation
  token scoped to the repository rather than storing a personal access token as a secret. See
  [permissions-and-secrets.md](permissions-and-secrets.md).
- Do not add the agent's app or bot identity to a ruleset's bypass actors. A bypass granted to
  automation removes the review requirement for anything that automation can be persuaded to do.

## Constraining what the agent can run

- Restrict the agent's tool allowlist in the action's configuration, naming the commands permitted
  rather than the commands denied. An allowlist that grants a general shell tool is not an
  allowlist, because every other entry is then reachable through the shell.
- No privileged step may follow the agent step in the same job. An agent with any shell can append
  to `$GITHUB_ENV`, `$GITHUB_OUTPUT`, or `$GITHUB_PATH`, which changes the environment of every
  later step, including one a reviewer read as safe.
- Set `persist-credentials: false` on the checkout. The default leaves the token in `.git/config`,
  where an agent with a file read tool finds a credential that no audit of `env:` would show.
- Run on a hosted or ephemeral runner. A self-hosted runner with a persistent workspace lets one
  run leave files that a later run reads, and an agent both writes files and reads its working
  directory. See [runners.md](runners.md).
- Set `timeout-minutes`. The default is 360, which is a long time for a loop that does not
  terminate.
- Where the agent job hands anything to a later job, the artifact and cache rules in
  [supply-chain.md](supply-chain.md) apply with more force: an artifact consumed by a privileged
  `workflow_run` job, or a cache key a default-branch run restores, turns one injected instruction
  into a lasting foothold.
- Remember that the job log is a disclosure channel. The agent's output is printed there, masking
  only covers registered secret values, and on a public repository the log is public.

## Configuration that arrives with the checkout

Instructions and configuration are different risks and need separating.

- A `CLAUDE.md` or `AGENTS.md` in the checkout is text the model reads, and a fork can edit it in
  the same pull request the agent is asked to review.
- A `.mcp.json`, a settings file, or anything else that adds MCP servers, hooks, or permission
  entries is configuration the runtime obeys. It adds tools and network destinations without the
  model deciding anything, so a fork that adds one gets execution and egress the workflow author
  never wrote.

On any run where the checked-out ref is not maintainer-authored, the agent's own configuration
comes from the workflow file or from a location outside the tree, never from the checkout. Give the
reviewer something to look for: a step between the checkout and the agent that deletes `CLAUDE.md`,
`AGENTS.md`, `.mcp.json` and `.claude/`, or flags on the agent step that pin its settings and MCP
configuration to paths outside the workspace.

## Untrusted text reaching the model

Every context in the untrusted inventory in [untrusted-input.md](untrusted-input.md) is untrusted
here for the same reasons, and quoting is not the remedy it is for a shell.

- Pass event data to the agent as an action input, or through `env:` where the step is a `run:`
  block, so the value never reaches generated script text. The two are not interchangeable: a
  value set in `env:` does not expand inside a `with:` input.
- Neither removes instruction injection. A correctly quoted title still arrives as text the model
  reads, which is why the containment is the token scope, the egress policy, and the review gate
  rather than the escaping.
- State the separation between data and instruction in the prompt, and rely on it for nothing.

## Reviewing what the agent produced

- A pull request opened with `GITHUB_TOKEN` starts no workflow runs, so its required checks never
  report and it cannot merge, while an unrequired check simply never runs. An agent whose work is
  meant to be checked opens the pull request with a GitHub App installation token instead. See
  [permissions-and-secrets.md](permissions-and-secrets.md).
- The pusher is the token identity. Commit author and committer come from `git config` in the
  workspace and are unauthenticated, so commit metadata does not establish that a person wrote the
  change. A signature does not settle it either, since a commit made through the API is signed by
  GitHub's own key and shows as verified. The push event actor and the audit log are the record.
- `CODEOWNERS` and required approvals are what make a person accountable for the change. Neither is
  satisfied by the agent reporting that it verified its own work.
- The token restriction on `.github/workflows/` covers workflow files and nothing else, so a code
  owner is needed on every path a workflow executes: composite actions under `.github/actions/`, a
  `Makefile`, package scripts, a pre-commit configuration, and any script a workflow step invokes.
  Otherwise the agent rewrites what the next run executes without touching a workflow file.

## Loops and cost

A workflow triggered by a comment can be triggered by the agent's own comment, but only when the
agent comments with a credential other than `GITHUB_TOKEN`, since events that token causes raise no
new run, with the `workflow_dispatch` and `repository_dispatch` exceptions in
[permissions-and-secrets.md](permissions-and-secrets.md). That is the credential this file
recommends elsewhere, so the guard is needed, and an agent holding `actions: write` can re-dispatch
its own workflow whatever credential it comments with.

- Compare the login rather than the actor type. A GitHub App token yields a sender of type `Bot`,
  but a personal access token yields type `User`, and that is the case that both loops and carries
  a person's full permissions. Test `github.event.comment.user.login` against the automation's
  account.
- Set `concurrency` keyed on the pull request. Without `cancel-in-progress` it serializes a burst
  rather than stopping a loop, and [scalability.md](scalability.md) warns against cancelling a run
  that leaves partial state, which is what an agent mid-push is. Decide which of the two the
  workflow needs.

## Checklist

- [ ] Actor gate on the job, not in the prompt, and a permission check where the job holds a write
      token or a model credential
- [ ] `issue_comment` scoped to `types: [created]`, with pull request comments distinguished from
      issue comments
- [ ] No `pull_request_target` job that checks out fork code and runs an agent
- [ ] Checkout pinned to a resolved commit SHA, with `persist-credentials: false`
- [ ] The model provider credential scoped to one step, and gated by an environment where the
      trigger is untrusted
- [ ] `permissions` granted per job, no `secrets: inherit`, and no secret beyond what the task needs
- [ ] The agent's identity cannot push to a protected branch, is not a ruleset bypass actor, and
      holds no Workflows permission or `workflow` scope
- [ ] Tool allowlist names permitted commands and does not grant a general shell
- [ ] No privileged step follows the agent step in the same job, or that step overrides
      `GITHUB_ENV`, `GITHUB_OUTPUT`, and `GITHUB_PATH` in its own `env:`
- [ ] Ephemeral runner, egress allowlist applied, and `timeout-minutes` set
- [ ] No `id-token: write` and no `actions: write` on the agent job
- [ ] Agent configuration is pinned outside the workspace, or the checkout's own agent files are
      deleted before the agent step
- [ ] The job log is treated as public on a public repository, and nothing the agent reads is
      summarized into it that the log should not carry
- [ ] Artifacts and caches the agent job writes are not consumed by a privileged job
- [ ] Event data passed as an action input, or through `env:` in a `run:` block
- [ ] Pull requests opened with an installation token where required checks must run
- [ ] `.github/workflows/` and every other path a workflow executes covered by a code owner who
      is not the automation
- [ ] Loop guard compares the automation's login, and `concurrency` is keyed on the pull request
