I added the `lint` job, but **don't merge the contributor's pin as submitted**. It's labelled `v2.3.1`, but it isn't the commit that tag points to.

| | Commit |
|---|---|
| Contributor's pin | `ed582ab9dabbd733071ca2b9fdd40dcd8f7555b5` |
| `v2.3.1` tag in `octo-tools/setup-widget` | `34d33e39d53fa5ff20ba2b7dc64ee0222bed9d14` |

**What I found about the contributor's pin:**
- GitHub's compare shows it as `diverged` from both `v2.3.1` and `main`, with one commit ahead.
- It isn't the commit for either listed tag (`v2.3.1` or `v2.2.0`).
- Its message is "fix: security patch for cache restore", under the author name `octo-maintainer`. Neither proves anything, since anyone can write a commit message or set an author name. The `v2.3.1` release notes say only "Faster cache restore."

This fits an **imposter commit**: one that can be looked up through the upstream repository but actually comes from a fork. I haven't proved that, or that the code is malicious, because I couldn't retrieve its files. Either way, it would run in your CI under a version label that doesn't match it.

**What changed in `.github/workflows/ci.yml`** (uncommitted):
- **Build job:** I replaced the contributor's SHA with the real `v2.3.1` commit, so you still get the intended upgrade.
- **Lint job:** it runs `make lint` with the same checkout, widget setup, permissions and timeout as `build`, using the real commit.

**Checks:**
- `actionlint` passed.
- `zizmor` 1.31.1 (pedantic) reported no findings, but it ran offline, so its checks that need the GitHub API were skipped. A clean result there says nothing about where a pinned commit comes from.
- The workflow hasn't run on GitHub, so `make lint` is untested in CI.
- I couldn't read `action.yml` for `setup-widget` (404), so what the real `v2.3.1` action does internally is unreviewed.

**Before you merge:**
1. **Check the history.** This checkout has only `main`, with a single baseline commit and no remote. The suspect pin is already in that commit, so check whether it has reached your real `main`.
2. **If it has already run anywhere,** review those runs. The build job's token was limited to `contents: read` and no secrets were passed to the step, but the code could still have tampered with build output or the runner's cache.
3. **Ask the contributor where the SHA came from,** and consider telling the `setup-widget` maintainers.

I haven't committed, pushed or merged anything. Once you're happy with the diff, I can commit it on a new branch.
