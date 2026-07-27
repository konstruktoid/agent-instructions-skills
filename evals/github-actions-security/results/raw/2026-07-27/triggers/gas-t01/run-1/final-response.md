I don't have write or shell tools available in this session (only Glob/Grep/Read/Skill), so I can't create the file or resolve action SHAs via `gh api` as the skill requires. Here's the workflow to add yourself at `.github/workflows/release.yml`, following the skill's baseline — you'll need to fill in the SHAs by running the two `gh api` lookups shown per action.

```yaml
name: Release

on:
  push:
    tags:
      - "v*"

permissions: {}

jobs:
  publish:
    name: Publish to npm
    runs-on: ubuntu-latest
    timeout-minutes: 10
    permissions:
      contents: read
      id-token: write   # for npm provenance
    steps:
      - name: Checkout repository
        uses: actions/checkout@<RESOLVE_SHA> # vX.Y.Z
        with:
          persist-credentials: false

      - name: Set up Node.js
        uses: actions/setup-node@<RESOLVE_SHA> # vX.Y.Z
        with:
          node-version: "20"
          registry-url: "https://registry.npmjs.org"

      - name: Install dependencies
        run: npm ci

      - name: Publish
        run: npm publish --provenance --access public
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

To resolve the two SHAs before using this:
```sh
gh api repos/actions/checkout/releases/latest --jq .tag_name
gh api repos/actions/checkout/commits/<tag> --jq .sha
gh api repos/actions/setup-node/releases/latest --jq .tag_name
gh api repos/actions/setup-node/commits/<tag> --jq .sha
```

Notes:
- `permissions: {}` at workflow level, `contents: read` + `id-token: write` at job level only — `id-token: write` enables `--provenance` attestation, but you still need an `NPM_TOKEN` secret with publish rights configured in the repo (or set up npm's OIDC trusted publishing on npmjs.com and drop the token entirely — worth considering since it removes a long-lived secret).
- `persist-credentials: false` since this job only reads code, never pushes.
- No `package.json` exists in this repo currently, so `npm ci` / `npm publish` will fail until one is added.

Once added, run `actionlint` and `uvx zizmor --persona=pedantic .` before merging — I wasn't able to run either here. Let me know if you'd like me to proceed differently, or if write/shell tools become available so I can create the file and verify it directly.
