I couldn't do the review. This session has no shell, so I can't run `gh api` against your organization. I also don't know your org's name, and my request to read the skill's policy reference file was declined. Nothing below comes from your org's actual data. It's the procedure, so you can run it or give me a session where I can.

## 1. List every installation (all pages)

```sh
ORG=your-org
gh api --paginate "orgs/$ORG/installations?per_page=100" --jq '.installations[] |
  {id, app_slug, repository_selection, permissions, events, created_at, updated_at, suspended_at}'
```

You need an org owner token for this. Leave `--paginate` in, or you'll only get the first page and the list will look complete when it isn't.

## 2. For each app, see which repos it can reach

- If `repository_selection` is `all`, the app reaches every repo, including ones created later. Treat that as the high-risk case.
- If it's `selected`, the repo list is easiest to check in the UI under **Settings → GitHub Apps → Configure**. Through the API, you'd need a token for that installation (`GET /installation/repositories`).

## 3. What to flag

| Finding | Why it matters |
|---|---|
| `repository_selection: all` along with any `write` permission | Any compromise or misuse reaches the whole fleet |
| `administration`, `organization_administration`, `members`, `secrets` or `actions` set to `write` | The app can change repo settings or membership, read secrets or run workflows |
| `contents: write` together with `workflows: write` | The app can push code and change CI, which is a supply-chain path |
| Permissions wider than the app's stated purpose | Narrow its scope or move it to `selected` |
| No clear owner, or `updated_at` / last use is old | Candidate for removal |
| `suspended_at` is set | Either finish removing it or record why it's kept |
| An app with pending permission upgrades | Someone approving these without review is how access quietly grows |

## 4. Related policy to check

- OAuth app access restrictions: **Settings → Third-party access → OAuth application policy**. They should be restricted, with approved apps listed.
- Who can install apps: members shouldn't be able to install them without owner approval.
- Personal access token policy: fine-grained tokens should need approval and have a maximum lifetime, and classic tokens should be restricted (`gh api orgs/$ORG/personal-access-tokens` lists approved fine-grained tokens).

## 5. Record it

For each app, write down its owner, the reason it's installed, its access scope, and a review date. Removing an app or narrowing its permissions changes access for the whole org. Confirm those changes separately; don't apply them as part of this review.

If you give me the org name and a session with shell access (with `gh` logged in as an org owner), I'll run the inventory and send you the findings app by app. If the token can't make some of the reads, I'll name those instead of reporting a clean result.
