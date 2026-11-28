I hardened `.github/workflows/assistant.yml`, but **don't enable it on the public repo yet**: `acme/coding-agent@v1` still needs pinning. A maintainer's PR comment still makes the agent change the code and push, except on fork PRs. The change is uncommitted.

**What was wrong**

The old workflow had no check on who was commenting. Anyone with a GitHub account could write instructions to an agent that held your model API key and a `write-all` token. It also checked out the PR's code, including code from strangers' forks, alongside those secrets.

**What I changed, and why**

| Change | Why |
|---|---|
| A separate `authorize` job, with no model key, requires the commenter to have write, maintain or admin access | This closes the main hole. `author_association` isn't enough, because org members and collaborators may not have write access. |
| Fork PRs are refused | Their files are controlled by outsiders and could steer an agent that holds secrets. |
| PRs that are closed, or whose head is the default branch, are refused | The agent shouldn't push to `main` this way. |
| Plain issues and bot comments are skipped | The old workflow also ran on ordinary issues. |
| Only `created` comments trigger it, not `edited` | Someone else can edit a maintainer's comment, and it still shows the maintainer as author. |
| `write-all` replaced with `contents: write` and `pull-requests: read` | The agent gets only what pushing and reading the PR need. |
| Checks out the PR's branch rather than `refs/pull/N/head` | The old ref left a detached HEAD with no branch to push to. |
| `actions/checkout` pinned to the same commit as `ci.yml` | A moved tag can't swap in different code. |
| 30-minute timeout and one run per PR | This limits runaway cost and stops two agents pushing over each other. |

**Behaviour differences**
- Fork PRs no longer work.
- The agent can no longer comment on PRs or issues, or use other permissions it had under `write-all`. If `acme/coding-agent` posts replies, add `pull-requests: write`.
- If several comments arrive while a run is in progress, only the newest waiting one is kept.

**Checks**
- `actionlint` passes.
- I ran the authorization script against a stubbed `gh` for admin, write, read, no access, closed PR, fork, deleted fork and default-branch head. Only admin and write on an open same-repo branch were allowed.
- The workflow has not run on GitHub, so try one real comment on a private copy.
- `zizmor` reports two high findings at its default settings:
  - `dangerous-triggers`: this is inherent in triggering from comments, and the authorization job is the mitigation.
  - `unpinned-uses`: this is the open item below.

**Before you enable it**
1. **Pin `acme/coding-agent`.** I couldn't resolve `v1` without credentials (the repo may be private or not exist), and I didn't want to guess a commit. Review the code, then replace `@v1` with its full commit SHA.
2. **Protect your branches and tags with rulesets.** `contents: write` isn't limited to the PR branch, so a misled agent could push elsewhere or create releases.
3. **Limit the model key.** Give it a spending cap. You could also move it into a GitHub environment restricted to the default branch, which means adding `environment:` to the `assistant` job.

**Remaining risks**
- **Prompt injection:** a maintainer may quote an outsider's text, or a branch may contain outside contributions. The agent could follow instructions hidden there while holding both the key and the write token.
- **Stored credential:** I kept the git credential in the checkout so the agent can push. A stronger design has the agent produce a patch and a separate job push it, but that depends on what `acme/coding-agent` supports.
- **CI on agent commits:** pushes made with `GITHUB_TOKEN` generally don't start CI automatically, so check those commits are tested before merging.

**Optional:** every comment from a maintainer on a same-repo PR still starts the agent, including "looks good". Requiring a prefix such as `/assistant` would prevent accidental runs. I didn't add it because it changes how you use the workflow.
