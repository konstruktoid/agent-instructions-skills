I added a Dependabot config and pinned every action reference to a commit SHA. I didn't run the workflows or commit anything.

- **Dependabot:** `.github/dependabot.yml` checks the `github-actions` ecosystem weekly. A `*` pattern in one group puts all action updates into a single pull request.
- **Pinning:** the six `uses:` lines in `ci.yml` and `codeql.yml` now use full SHAs with a version comment. Dependabot updates both the SHA and the comment, so the pins stay current.

  | Action | Pinned to |
  |---|---|
  | `actions/checkout` | v5.1.0 |
  | `astral-sh/setup-uv` | v6.8.0 |
  | `github/codeql-action` (`init` and `analyze`) | v3.39.1 |

  Each SHA is the commit the old major tag pointed to when I looked it up. For `setup-uv` and `codeql-action`, the tags are annotated, so I resolved them to the underlying commits rather than using the tag-object SHAs.
- **README:** the line saying there was no Dependabot configuration is gone. A new "How action updates are handled" section explains the SHA pinning, the weekly grouped pull request, and that new actions should be pinned the same way.
