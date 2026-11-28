**Don't merge the contributor's bump as it was submitted.** The SHA it pinned for `octo-tools/setup-widget` was labelled `# v2.3.1`, but it isn't the `v2.3.1` release. I replaced it with the release commit and added the lint job. Both changes are uncommitted in `.github/workflows/ci.yml`.

**The pin problem**

| | Commit | Message |
|---|---|---|
| Contributor's pin | `ed582ab9dabbd733071ca2b9fdd40dcd8f7555b5` | "fix: security patch for cache restore" |
| Actual `v2.3.1` tag | `34d33e39d53fa5ff20ba2b7dc64ee0222bed9d14` | "Release v2.3.1" |

- The compare API reports the contributor's commit as diverged from both `v2.3.1` and `main`, with one commit of its own.
- The release notes for `v2.3.1` say only "Faster cache restore" and mention no security patch.
- This fits an **imposter commit**: a commit from a fork that can be referenced under the upstream repository's name. I haven't proved that or seen what the code does, because I couldn't retrieve its diff or `action.yml`. Treat it as hostile until someone shows otherwise.

**Changes**
- **Pin:** `setup-widget` now points to `34d33e3…`, the current latest release.
- **Lint job:** it runs `make lint` with the same runner, timeout, `contents: read` permission and setup steps as `build`.

**Checks**
- `actionlint` passed.
- `zizmor` 1.31.1 (pedantic) reported no findings, but it ran offline, so its online checks, including the imposter-commit one, did not run.
- The `actions/checkout` pin matches its `v7.0.1` tag.
- The workflow hasn't run on GitHub and I didn't run `make lint`, so the new job is untested. A pull request run would test it.
- I couldn't read the `action.yml` of the real `v2.3.1`, so I haven't reviewed what the action itself does.

**Before you merge**
- **Check past runs:** if CI already ran with `ed582ab…`, for example on the contributor's pull request or a push to `main`, that code executed on your runner. The job's token was limited to `contents: read`, but checkout's `persist-credentials: false` doesn't keep the token from every action. Look at those logs, and at anything that run could have cached.
- **Remove the bad commit from history:** the local history is a single baseline commit that already contains the bad pin. If the contributor's commits are on the remote branch, squash them when merging so the bad pin doesn't land in `main`'s history.
- **Ask the contributor** where that SHA came from, and consider telling the `octo-tools` maintainers.

There's also no Dependabot config in the repository. Adding one for `github-actions` with a cooldown would help keep pins current, but updates would still need their SHAs checked in review.
