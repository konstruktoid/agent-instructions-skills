I rewrote `.github/workflows/assistant.yml`, but **don't enable it yet**: the agent action still isn't pinned, and I haven't run the workflow on GitHub.

**What was wrong**
- **Anyone could run it.** Any GitHub user's comment started an agent with `write-all` permissions and your model API key, told to push whatever the comment asked.
- **Fork code ran next to your secrets.** It checked out any PR's head, including forks, so a stranger's files could steer the agent.
- **The agent held a write token.** A manipulated agent could do anything that token allowed.

**What I changed, and why**

| Change | Why |
|---|---|
| New `authorize` job requires `write` or `admin` permission, checked through the API | Only people who could push anyway can trigger it |
| Only open PRs from branches in this repository, never from the default branch | Keeps fork code out and stops direct pushes to `main` |
| Plain issues and bot comments are ignored | The request was for people commenting on PRs |
| `edited` trigger removed | Someone else can edit a maintainer's comment, and it still looks like the maintainer's |
| Agent job is read-only; a separate `push` job applies its patch | The agent never gets a token that can write to the repository |
| Checkout uses the commit recorded by `authorize`, and the push fails if the branch has moved | Newer commits aren't overwritten |
| `write-all` replaced with per-job permissions, plus timeouts and `persist-credentials: false` | Least privilege |
| `checkout` and the artifact actions pinned to commit SHAs | Tags can be moved |

**Behaviour differences**
- A maintainer still comments and the change gets pushed, but the workflow now does the commit and push, not the agent. The commit message is generic and links to the comment.
- Fork PRs and edited comments no longer work. For an edit, post a new comment.
- If two requests overlap on one PR, the later push can be rejected; comment again.

**Before you enable it**
1. **Pin `acme/coding-agent`.** I couldn't list any tags for it from here (it may be private or a placeholder). Review its source and replace `@v1` with a full commit SHA; there's a `TODO` at that step.
2. **Check that the action works this way.** I assumed it edits files in the checkout, works with a read-only `GH_TOKEN`, and doesn't need to push. If it only works by pushing or calling the API itself, the split needs adjusting.
3. **Try it on a test PR.**

**What I tested**
- `actionlint` passes.
- `zizmor` still reports two high findings: the unpinned agent action, and the `issue_comment` trigger itself. I kept the trigger because your feature depends on it, with the checks above guarding it.
- I ran the shell steps locally with a stand-in for `gh`. Writers and admins were allowed; readers, non-collaborators, API errors, closed PRs, forks and the default branch were blocked.
- A patch with a commit, an edit, a deletion and a binary file pushed correctly to a local repository, and a push to a moved branch was rejected.

**Remaining risks**
- **API key:** the agent still has `MODEL_API_KEY` and reads PR content, so injected instructions could try to leak it, including through the patch artifact, which others may be able to download. Use a dedicated key with a spending limit.
- **Review the agent's commits:** a patch can change anything on the branch that the token is allowed to push, including the `Makefile` that CI runs. Pushes made with `GITHUB_TOKEN` don't normally trigger CI, so don't rely on an earlier green check.
- **Every maintainer comment triggers it,** even "looks good", as before. I'd add a prefix such as `/assistant`; I didn't, because it changes how you use it.
- **Repository settings:** consider branch protection on `main` and any release branches. You could also move the key into an environment with required approval, at the cost of an extra click per run.

The changes are uncommitted in your working tree.
