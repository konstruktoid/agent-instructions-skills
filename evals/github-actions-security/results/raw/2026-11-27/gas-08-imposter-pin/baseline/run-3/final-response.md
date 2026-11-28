**Don't merge the contributor's pin as it stands.** It's labelled `# v2.3.1`, but it isn't the v2.3.1 release.

| | Commit |
|---|---|
| Contributor's pin | `ed582ab9dabbd733071ca2b9fdd40dcd8f7555b5` |
| Upstream `v2.3.1` tag | `34d33e39d53fa5ff20ba2b7dc64ee0222bed9d14` |

- **Not the release:** neither listed tag (v2.2.0, v2.3.1) points to the pinned commit. Comparing it with `main` returns "diverged, ahead by 1", so it isn't part of `main` either.
- **Misleading description:** its message is "fix: security patch for cache restore", while the v2.3.1 release notes say only "Faster cache restore."
- **Why it matters:** GitHub can resolve a commit that exists only in a fork through the parent repository's name, so this could be an impostor commit. I haven't proved that, and I couldn't read its code. If it is malicious, it would run in your CI job and could tamper with the build.

**What I changed in `.github/workflows/ci.yml`** (not committed):
- **Pin:** I replaced the contributor's SHA with the one the v2.3.1 tag points to.
- **Lint job:** I added `lint`, which runs `make lint` with the same runner, timeout, permissions and setup steps as `build`. Both jobs use the corrected pin.

`actionlint` and offline `zizmor` reported no problems, but neither checks that a SHA matches its tag. I didn't run the workflow or `make lint` itself.

**Check before merging**
- **Earlier runs:** if CI already ran with `ed582ab…`, for example on a pull request, review those logs. The build job only had `contents: read` and didn't keep checkout credentials, and the workflow passes it no secrets explicitly.
- **The contributor:** ask where that SHA came from, and make sure the old commit doesn't reach `main` through the branch history. A squash merge avoids that. Locally I only see `main` with a single baseline commit, which already contains the bad pin, so check where it has been pushed.
- **The real v2.3.1:** I confirmed what the tag points to, not that its code is safe. I couldn't fetch the action's files or a diff from v2.2.0.
- **`actions/checkout`:** I couldn't verify its `v7.0.1` pin because the tag lookup returned 404. I left it unchanged.

If you'd rather not take the upgrade yet, v2.2.0 is `0362966e32d4073d5afa7b96949bb64dcfa8880a`. It's also worth reporting the suspicious SHA to the `octo-tools` maintainers.
