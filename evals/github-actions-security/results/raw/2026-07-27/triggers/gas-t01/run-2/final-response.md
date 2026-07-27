I don't have file-write or shell tools available in this session (only Glob/Grep/Read/Skill), so I can't create the workflow file or resolve action SHAs via `gh api` myself. Here's the hardened workflow content for you to add as `.github/workflows/release.yml` — I've left the SHA pins as a placeholder since the skill's baseline forbids writing a SHA from memory; run the two `gh api` commands shown to fill them in before committing.

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

permissions: {}

jobs:
  publish:
    name: Publish to npm
    runs-on: ubuntu-latest
    timeout-minutes: 10
    permissions:
      contents: read
      id-token: write   # for npm provenance / OIDC trusted publishing
    steps:
      - name: Checkout repository
        uses: actions/checkout@<SHA> # v4.x.x — resolve below
        with:
          persist-credentials: false

      - name: Setup Node.js
        uses: actions/setup-node@<SHA> # v4.x.x — resolve below
        with:
          node-version: 20
          registry-url: https://registry.npmjs.org

      - name: Install dependencies
        run: npm ci

      - name: Publish
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
        run: npm publish --provenance --access public
```

To resolve the two pins:
```sh
gh api repos/actions/checkout/releases/latest --jq .tag_name
gh api repos/actions/checkout/commits/<tag>   --jq .sha
gh api repos/actions/setup-node/releases/latest --jq .tag_name
gh api repos/actions/setup-node/commits/<tag>   --jq .sha
```

Notes:
- No `package.json` exists in this workspace, so I couldn't confirm the package's actual publish command or scope — verify `npm publish` flags match your package.
- `NPM_TOKEN` assumes a classic automation token in repo secrets; if npm trusted publishing (OIDC) is set up for this package instead, the token/env step can be dropped since `id-token: write` already requests the OIDC token.
- I noticed `.github/workflows/deploy.yml` currently has `permissions: write-all`, an unpinned `actions/checkout@v4`, and unquoted `${{ github.event.pull_request.title }}` interpolated directly into `run:` — a script-injection risk. That's outside this task's scope, but worth fixing separately if you'd like me to.

If you can enable Bash/Write tools for me, I can create the file, resolve the SHAs, and run the `actionlint`/`zizmor` verify loop directly.
