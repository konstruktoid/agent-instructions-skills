I rewrote `.github/workflows/assistant.yml`. A maintainer still comments on a pull request and the change gets pushed to its branch. **Don't enable it on the public repository yet:** the agent action isn't pinned, and nothing has run on GitHub.

**What was wrong**
- **Anyone could run it.** Any GitHub user's comment started an agent holding your model key and a `write-all` token, and their text was its instructions.
- **Fork code ran with those credentials.** It checked out the pull request head, forks included.
- **The checkout left the token on disk**, where the agent could read it.

**What I changed**

| Change | Why |
|---|---|
| Split into `gate`, `agent` and `push` jobs | The agent gets a read-only token and hands over a patch. Only trusted script pushes it. |
| `gate` requires `write`, `maintain` or `admin` | The comment's "author association" label alone also admits people with read-only access. |
| Fork, closed and default-branch pull requests are refused | Keeps outside code away from the model key and avoids pushing to `main`. |
| Agent works from a fixed commit; the push fails if the branch has moved | It can't overwrite or restore commits it never saw. |
| `push` rejects changes under `.github/` | Stops the agent rewriting automation or repository policy files. |
| Only new comments trigger it, not edits | Someone else can edit a maintainer's comment and re-run it under that name. |
| Per-job permissions, timeouts, one run per pull request | Limits damage, cost and overlapping pushes. |
| `checkout` updated to v7.0.1; all `actions/*` references pinned by commit SHA | Tags can be moved. |

**Behaviour differences**
- Fork pull requests no longer work, which matters on a public repository.
- The agent can no longer push or comment itself. It edits files, and the workflow commits them with a fixed message.
- Refused requests show up as failed runs with the reason.

**Checks**
- `actionlint` passes.
- I ran the gate, patch and push scripts locally against a fake `gh` and a local remote. Allowed, refused, empty, `.github/`, binary-file and moved-branch cases behaved as expected.
- `zizmor` (offline) still reports two high findings on this file, neither suppressed:
  - `dangerous-triggers`: comes with using comments as the interface; the gate is what contains it.
  - `unpinned-uses`: `acme/coding-agent@v1`, explained below.

**Before you enable it**
1. **Pin `acme/coding-agent`.** I couldn't read its repository, so there's a `FIXME` instead of a SHA. Whoever controls that tag controls code that receives your model key.
2. **Check how that action behaves.** I don't know whether it works with a read-only token and just edits files, or insists on pushing or commenting. Also look for a setting that limits which commands it can run, and use it.
3. **Do a test run on a private copy.** This covers the permission lookup (I gave `gate` `contents: write` for it), the artifact handoff and the real push.
4. **Protect `main` and release branches with rulesets.**

**Risks that remain**
- **Key theft:** text in the repository or pull request can still steer the agent. It has your model key and unrestricted network access, so it could leak the key, including into the patch or the public log. Use a dedicated key with a spending limit.
- **Other files it can change:** it can still edit things CI executes, such as the `Makefile`. Review its commits before merging.
- **CI doesn't run on its commits:** pushes made with `GITHUB_TOKEN` don't start workflows, as before. Don't treat an earlier green check as covering them.
- **Bot branches:** branches in your own repository are trusted, including ones opened by bots such as Dependabot.

**Optional, not done**
- **Command prefix:** every maintainer comment on a pull request still starts the agent, even "LGTM". Requiring something like `/assistant` would stop that.
- **Approval step:** putting the key in an environment with required reviewers would add a human check before each run.
- **`ci.yml`:** I didn't touch it. It pins an older `checkout` (v5.0.0).
