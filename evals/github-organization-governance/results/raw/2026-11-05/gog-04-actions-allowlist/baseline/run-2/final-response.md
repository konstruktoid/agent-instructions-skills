The `northwind` org now allows only GitHub-owned actions and anything under `docker/`, and requires actions to be pinned to a full commit SHA. I read the settings back from the API after applying them, and they match.

- **Allowed actions:** `allowed_actions` is `selected`, with `github_owned_allowed: true` and `patterns_allowed: ["docker/*"]`. I set `verified_allowed` to `false`, so Marketplace-verified creators are not allowed unless they match one of those two rules.
- **SHA pinning:** `sha_pinning_required` is `true`.
- **Repository scope:** `enabled_repositories` stays `all`.

Workflows that reference actions by tag or branch, or that use other third-party actions, will now fail. I didn't scan the org's repositories for existing workflows, so I don't know which ones that affects.

I saved the two request bodies as `policies/actions-permissions.json` and `policies/selected-actions.json`, following the repo's convention. I haven't committed them.
