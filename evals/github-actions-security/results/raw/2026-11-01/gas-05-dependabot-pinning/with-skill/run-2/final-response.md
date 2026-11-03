I added `.github/dependabot.yml` and pinned every action reference to a commit SHA, so the workflows match how Dependabot will maintain them. I did not push or run the workflows. `actionlint` and `zizmor` (pedantic) both came back clean.

**Dependabot config**
- It checks the `github-actions` ecosystem weekly.
- A single group matching `*` puts every update in one pull request.
- I added a 7-day cooldown, which you didn't ask for. It holds back brand-new releases so a malicious one has time to be caught.

**Pinned actions**
I looked up each action's latest release and its commit SHA instead of reusing the old versions. Each version comment is in the form Dependabot rewrites.

| Action | Was | Now |
|---|---|---|
| `actions/checkout` | `@v5` | `3d3c42e5…` # v7.0.1 |
| `astral-sh/setup-uv` | `@v6` | `07a047e6…` # v10.3.2 |
| `github/codeql-action/init` and `/analyze` | `@v3` | `9b325408…` # v4.39.1 |

- **setup-uv:** The newest release is v10.3.3, from 4 days ago. That is inside the 7-day cooldown, so I pinned v10.3.2 instead.
- **codeql-action:** `releases/latest` returned a CodeQL bundle marker, not an action release. I took v4.39.1 from the tags, and the releases list shows it as a real release.
- **Major bumps:** All three are major-version jumps (checkout 5→7, setup-uv 6→10, codeql 3→4). I skimmed the release notes for the breaking changes. They concern fork pull requests under `pull_request_target`, cache behavior on certain events, and SARIF handling. None of the three applies to these workflows, which use `pull_request`, `push` and `schedule`. I haven't run them, so treat the bumps as untested until CI runs.

**Zizmor findings**
Zizmor flagged three low findings. I added a workflow-level `concurrency` group to `ci.yml` and `codeql.yml`, and a comment on `security-events: write` explaining it uploads CodeQL results.

**README**
It now explains the SHA pinning, the weekly grouped pull request, the cooldown, and how to review the weekly pull request.

I haven't committed anything.
