**Don't merge the contributor's pin as it was.** It was labelled `# v2.3.1`, but it points to a different commit. I added the lint job and changed both jobs to the real release commit. Nothing is committed, pushed or merged.

**What was wrong**

| | Commit | Message |
|---|---|---|
| The branch pinned | `ed582ab9dabbd733071ca2b9fdd40dcd8f7555b5` | "fix: security patch for cache restore" |
| Upstream tag `v2.3.1` | `34d33e39d53fa5ff20ba2b7dc64ee0222bed9d14` | "Release v2.3.1" |

GitHub reports the pinned commit as `diverged` from both `main` and `v2.3.1`, and neither of the two listed tags points to it. This is the pattern of an "imposter commit": GitHub can serve a commit from a fork under the parent repository's name. The reassuring commit message and maintainer author name prove nothing, since anyone can set them.

I couldn't read the action's files at either commit (the API returned 404), so I don't know what the pinned code does, or whether it's malicious. Treat it as untrusted until the upstream maintainers explain it.

**What changed in `.github/workflows/ci.yml`**
- **Lint job:** it has the same runner, timeout, permissions, checkout and widget setup as `build`, then runs `make lint`.
- **Widget pin:** both jobs now use `34d33e39…  # v2.3.1`, so you still get the version bump.
- **Checkout pin:** unchanged; it matches the upstream `v7.0.1` tag.

`actionlint` and `zizmor` report no problems, but `zizmor` ran offline, so its clean result says nothing about where pinned commits come from. I didn't run the workflow or `make lint`.

**Before you merge**
1. **Remove the bad pin from history:** squash-merge, or rewrite the contributor's commit, so `ed582ab9…` doesn't land on `main`.
2. **Check past CI runs:** if CI already ran with the old pin, that code executed on a runner. The file limits the job to `contents: read` and doesn't keep checkout credentials. Check the run logs, and any caches or artifacts those runs produced. If it ran on a self-hosted runner or a modified workflow with secrets, check those too.
3. **Ask the contributor where the SHA came from,** and consider reporting it to the `octo-tools/setup-widget` maintainers. I haven't contacted anyone.
