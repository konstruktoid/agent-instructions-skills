I added `.github/dependabot.yml` and pinned every action in both workflows to a full commit SHA. I haven't run the workflows or committed anything.

- **Dependabot config:** it checks the `github-actions` ecosystem at `/` weekly. A group with the pattern `*` combines all action updates into one pull request.
- **Pinning:** each `uses:` line is now `owner/action@<sha> # vX.Y.Z`. Dependabot updates both the SHA and the version comment.
- **README:** the new "Action updates" section replaces the old "no Dependabot" line. It describes the SHA pins, the weekly grouped PR, and the rule to pin any new action to a SHA with a version comment.

I looked up the SHAs with `git ls-remote` against the upstream repos. For the annotated tags, I used the commit the tag points to rather than the tag object.

| Action | Previous ref | Now pinned to |
|---|---|---|
| `actions/checkout` | `v5` | v5.1.0 |
| `astral-sh/setup-uv` | `v6` | v6.8.0 |
| `github/codeql-action` (`init` and `analyze`) | `v3` | v3.38.2 |

Each pin points at the same commit its major tag did when I looked, so the first Dependabot PR shows only real upstream changes.
