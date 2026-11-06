The `northwind` org's Actions policy is now restricted and I read it back from the API to confirm.

- **Allowed actions:** only GitHub-owned actions and anything matching `docker/*`. Verified-creator actions are off.
- **SHA pinning:** required, so every action must be pinned to a full commit SHA.
- **Repositories:** still enabled for all of them (unchanged).

I saved the two request bodies in `policies/` as `actions-permissions.json` and `actions-selected-actions.json`. I haven't committed them.

Workflows in the org that use tag- or branch-pinned actions, or actions from other owners, will fail until they're updated.
