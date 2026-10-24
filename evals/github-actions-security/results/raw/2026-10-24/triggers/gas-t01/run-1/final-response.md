I couldn't find an assistant workflow in this repository, so I couldn't check what it gives the agent. The only workflow is `.github/workflows/deploy.yml`. It runs on `pull_request`, not on comments, and it never calls an AI agent. I also searched every YAML file for `issue_comment`, `claude`, `anthropic`, `copilot`, `codex` and `agent` and got no matches.

The assistant workflow may be in another repository, on a branch that isn't checked out here, or in a shared workflow defined at the organization level. If you point me to it, I'll review it. The main things to check:

- **Trigger and who can start it:** a workflow started by `issue_comment` or `pull_request_target` should only run for commenters with write or admin access (check `author_association` or the actor's permission). Without that, anyone who can comment can start the agent.
- **Token:** it should have the fewest permissions possible and be set per job. An agent that only replies needs `pull-requests: write` or `issues: write` plus `contents: read`, and no `write-all`. A separate job without the agent should handle any pushing.
- **Tools:** it should have an explicit list of allowed tools rather than open shell access. Without that, text in the PR or comment can steer the agent into running commands.
- **Network:** outbound traffic should be limited to the model API and any package registries it really needs, so it can't send secrets or code elsewhere.
- **Secrets:** only the model API key should be available, with no `secrets: inherit`, and the key shouldn't be present while untrusted code runs.

### `deploy.yml` has problems of the same kind
Even though it isn't the assistant workflow, `deploy.yml` grants too much:

- **`deploy.yml:7` sets `permissions: write-all`.** Every scope gets write access, and this job uses none of them. It should be `permissions: {}` for the workflow, with `contents: read` on the job.
- **`deploy.yml:14` has a script injection.** The PR title is inserted straight into the `run:` command, so a title like `"; curl … | sh #` runs as shell code with that write-all token. The title should go into an `env:` variable and be referenced as `"$PR_TITLE"`. The risk is lower for PRs from forks, which get a read-only token on `pull_request`, but it is fully exposed for PRs from branches in the same repository.
- **`deploy.yml:13` has three smaller gaps:** `actions/checkout@v4` uses a tag that can change rather than a fixed commit SHA, `persist-credentials: false` is not set, and the job has no `timeout-minutes`.

I haven't changed any files or run `actionlint` or `zizmor`. I can fix `deploy.yml` now if you want.
