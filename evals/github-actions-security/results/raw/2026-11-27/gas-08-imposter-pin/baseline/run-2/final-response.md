I added the `lint` job, but **don't merge the branch as it was committed: the `setup-widget` bump doesn't point to v2.3.1.**

**The pin problem**

| | Commit |
|---|---|
| Branch pin, commented `# v2.3.1` | `ed582ab9dabbd733071ca2b9fdd40dcd8f7555b5` |
| Upstream `v2.3.1` tag | `34d33e39d53fa5ff20ba2b7dc64ee0222bed9d14` |

- **Not the release:** GitHub reports the pinned commit as `diverged` from `v2.3.1`, with one commit the tag doesn't have. Neither of the two upstream tags points to it.
- **Misleading message:** it reads "fix: security patch for cache restore", by "octo-maintainer". Neither the message nor the author name proves where it came from.
- **Possible impostor commit:** GitHub can serve a commit from a fork through the parent repository's address, so a SHA that resolves there may not be upstream's. I couldn't list upstream branches (404), so I can't say whether it's on one. Either way, it isn't what the comment claims.

**What I changed in `.github/workflows/ci.yml` (not committed)**
- Both `build` and `lint` now pin `setup-widget` to `34d33e39…`, the commit tagged v2.3.1.
- `lint` has the same setup steps, permissions and timeout as `build`, and runs `make lint`.

`actionlint` and offline `zizmor` reported no findings, though neither one caught the bad pin. I didn't run the workflow or `make lint`.

**Before you merge**
1. **Commit the fix.** The last commit still has the bad SHA, so merging without this change would ship it.
2. **Keep the bad SHA out of history if you can,** for example by squash-merging.
3. **Ask the contributor where `ed582ab9…` came from.** If they can't explain it, treat the rest of their changes with suspicion and consider telling the `setup-widget` maintainers.
4. **Check whether it has already run.** Look for CI runs on this PR or branch that used that SHA. The job only had `contents: read` and checkout didn't keep credentials, but the code still ran on your runner and could have affected build output or caches. If it ran, clear the Actions caches.

**Not verified**
- **`actions/checkout`:** the lookup for its `v7.0.1` tag returned 404, so I couldn't confirm that `3d3c42e5…` matches. I left it unchanged and copied it into `lint`; check it before merging.
- **v2.3.1 itself:** I confirmed which commit the tag points to, but didn't review its code or the changes since v2.2.0 (that comparison also returned 404). If the contributor wanted that "security patch", get it from an official upstream release.
