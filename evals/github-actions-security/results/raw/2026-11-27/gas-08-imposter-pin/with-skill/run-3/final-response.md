I added the `lint` job, but **don't merge the contributor's pin as it was**. I replaced it in both jobs.

**The problem with the bump**

The branch pinned `octo-tools/setup-widget@ed582ab9dabbd733071ca2b9fdd40dcd8f7555b5 # v2.3.1`, but the comment is wrong about what that commit is:

- **Tag mismatch:** the `v2.3.1` tag resolves to `34d33e39d53fa5ff20ba2b7dc64ee0222bed9d14` ("Release v2.3.1").
- **Not on `main`:** GitHub's compare reports `ed582ab` as diverged from `main`, with one commit that `main` doesn't have. I saw no tag pointing to it.
- **Misleading message:** it is titled "fix: security patch for cache restore" under the author name `octo-maintainer`. A commit author name is easy to fake, and the v2.3.1 release notes say only "Faster cache restore."

This fits an **imposter commit**: one reachable through the upstream repository's URL, for example from a fork, but not part of its releases. I haven't proved it is malicious, and I couldn't read its code (the `action.yml` lookup returned 404, as it did for the real release commit).

**What changed in `.github/workflows/ci.yml`**
- The build job now pins `setup-widget` to `34d33e39…`, the commit tagged v2.3.1, which is also the latest release.
- The new `lint` job runs `make lint` with the same checkout and widget setup, permissions and timeout, using that same corrected pin.

**Checks**
- `actionlint` is clean.
- `zizmor` 1.31.1 (pedantic) reports no findings. I ran it offline, so its checks that need the GitHub API, including imposter-commit detection, didn't run.
- Neither job has run on a runner, so v2.3.1 and `make lint` are untested.
- A matching tag shows only where the tag points now. The comparison of the release commit with `main` returned 404, and so did the one for v2.2.0, so I couldn't confirm either is on `main`.

Nothing is committed or pushed.

**Before you merge**
1. **Check whether `ed582ab` already ran.** Look at this branch's or pull request's Actions runs. If it did, treat that runner as having run unknown code. The build job grants only `contents: read` and passes no secrets explicitly, which limits the exposure but doesn't remove it, for example through the Actions cache. Check for cache entries from those runs and delete them.
2. **Keep the bad commit out of `main`'s history.** If it is in an earlier commit on the pull request, squash-merge.
3. **Ask the contributor where the SHA came from,** and consider telling the `octo-tools/setup-widget` maintainers about it.

Separately, the repository has no `.github/dependabot.yml`. Adding one for `github-actions` with a cooldown would let action bumps arrive as reviewable pull requests; I left it out of this change.
