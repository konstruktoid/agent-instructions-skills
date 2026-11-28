I rewrote `.github/workflows/assistant.yml`. A maintainer can still comment on a PR and have the change made and pushed, with the limits below. **Don't enable it publicly until you've pinned the agent action and done one real run.**

## What was wrong
- **Anyone could run it.** Any GitHub user could comment and direct an agent that had your model API key and a `write-all` token. This was the serious one.
- **Fork code ran with those privileges.** It checked out the PR head, including forks, so a stranger's files could steer the agent.
- **The agent could write to the repository.** A successful prompt injection could have done anything the token allowed.

## What I changed

| Change | Why |
|---|---|
| Only users with `write` or `admin` permission can run it; bots are ignored | `author_association` would also let in some people with read-only access |
| Fork PRs, closed PRs and PRs whose head is the default branch are refused | Keeps outside code away from the secret and protects `main` |
| Plain issue comments are ignored | The old workflow tried to check out a PR that didn't exist |
| Removed the `edited` trigger | Someone else can edit a maintainer's comment and start a run under the maintainer's name |
| Split into `authorize`, `agent` and `push` jobs | The agent only has read access; a separate job that runs no repository code pushes its patch |
| `write-all` replaced with per-job permissions | Only `push` can write, and only to repository contents |
| Checkout uses a fixed commit SHA and stores no credentials | The agent works on a known commit and finds no git token on disk |
| Push is rejected if the branch moved, or if the patch touches `.github/` | Avoids overwriting newer work, or changing workflows and repository config |
| Added timeouts, one agent run per PR, and pinned actions | Limits runaway cost and tag-swapping |

## Behaviour differences
- The agent is now told to edit files only, and the workflow makes a single commit.
- It no longer gets `GH_TOKEN`, so it **can't comment on the PR or call the GitHub API**. If you rely on that, we need to add it back deliberately.
- Refused or no-op runs show only a notice in the Actions log.
- Two quick comments on one PR can overlap with the first run's push, in which case the second push is rejected and you'd comment again.

## Testing
- `actionlint` passes.
- `zizmor` reports two high findings:
  - `dangerous-triggers`: `issue_comment` is needed for this feature, and the permission check is the mitigation.
  - `unpinned-uses`: the agent action, covered below.
- I ran the shell scripts locally with a fake `gh` and a local git remote. Allowed and refused cases, normal and agent-committed changes, no changes, a `.github/` edit and a moved branch all behaved as expected.
- **Nothing has run on GitHub.** I haven't verified that `acme/coding-agent` works without `GH_TOKEN` or follows the instruction not to push.

## Before you turn it on
1. **Pin `acme/coding-agent@v1` to a commit SHA.** I couldn't look it up, because GitHub asked for credentials (it may be private or not exist). Check what that version does, including which tools it lets the agent use.
2. **Use a dedicated API key with a spending limit.** The agent still holds `MODEL_API_KEY`, and injected text from the repository or the comment could try to leak it.
3. **Treat logs and the patch as public.** The patch is kept as an artifact for one day.
4. **Review agent commits and run CI yourself.** Pushes made with `GITHUB_TOKEN` don't trigger your `ci` workflow, as was already the case.
5. **Be careful with caching in other workflows.** The agent job runs in the default branch's context, so a compromised agent could poison the Actions cache. Don't let release or deploy jobs trust it.

## One decision for you
Every comment a maintainer makes on an eligible PR still starts the agent, including "LGTM" or a reply quoting an outsider's text. I'd require a prefix such as `/assistant`, but left it out because it changes how you use it. It's one more condition on the `authorize` job:

```yaml
startsWith(github.event.comment.body, '/assistant ')
```

The changes are uncommitted in your working tree. The workflow takes effect once it's on the default branch.
