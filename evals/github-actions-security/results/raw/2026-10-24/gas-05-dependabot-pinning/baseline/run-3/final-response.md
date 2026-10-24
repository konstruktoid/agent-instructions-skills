I added a Dependabot config and pinned every action reference to a commit SHA. I didn't run any workflows, and nothing is committed.

- **Dependabot:** `.github/dependabot.yml` watches the `github-actions` ecosystem at `/` every week. A single `github-actions` group (pattern `*`) puts all updates in one pull request.
- **Pinning:** All six `uses:` lines in `ci.yml` and `codeql.yml` now point to the commit SHA that each major tag resolved to today, with a trailing comment like `# v5`. Dependabot keeps both the SHA and the comment current, which it can't do for a bare tag like `@v5` without moving it to a newer major.
- **Tag resolution:** I looked the SHAs up with `git ls-remote`. `setup-uv` v6 and `codeql-action` v3 are annotated tags, so I used the underlying commit SHAs, not the tag-object SHAs.
- **README:** The old "no Dependabot" line is replaced by an "Action updates" section. It explains the SHA pinning, the weekly grouped Dependabot PR, to review and merge that PR instead of bumping versions by hand, and to pin new actions the same way.
