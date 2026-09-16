**Files changed:** `.github/workflows/ci.yml`, `README.md`, `.github/dependabot.yml` (new).

**What was added:**
- `release` job: triggered by `v*` tags, gated with `needs: build` and `if: startsWith(github.ref, 'refs/tags/v')`, so it only runs after `build` passes on that same tag's workflow run. Builds via `npm run build`, publishes with `npm publish` (`NPM_TOKEN` → `NODE_AUTH_TOKEN`), then `gh release create` for the tag.
- `build` job unchanged in behavior; only its trigger now also fires on tag pushes (needed for `needs: build` gating to work) and got `permissions: {}`-workflow / `contents: read`-job, SHA pinning, `timeout-minutes`, `persist-credentials: false`, disabled implicit `setup-node` caching.
- `.github/dependabot.yml`: weekly `github-actions` updates with a 7-day cooldown, so the new SHA pins don't go stale.
- README: replaced the hand-cut process with the tag-push instructions.

**Deliberate exception:** you asked specifically for `NPM_TOKEN`-based publishing rather than npm's OIDC trusted publishing, which zizmor flags (`use-trusted-publishing`, informational). Documented inline at ci.yml:66-67 and here per the skill's rule on stated exceptions — trusted publishing would remove the stored token if you want to revisit it later.

**Verify loop:** 2 attempts, converged.
- `actionlint`: clean, both attempts.
- `zizmor --persona=pedantic`: attempt 1 found 2 high (cache-poisoning from setup-node's default `package-manager-cache`), 2 low/help, 1 info; attempt 2, after disabling that cache and adding `concurrency` + a permissions comment, is clean except the one informational, deliberate exception above.
- **Not run on a runner.** This is a behavioral gap, not a structural one: I have not pushed a branch or a tag, so the trigger wiring, `needs` gating, and the actual npm publish / release creation are unverified. Exercising it requires pushing a `v*` tag (or a `workflow_dispatch` test), which I won't do without your go-ahead since it would publish a real package version and create a real release using your `NPM_TOKEN`.

Want me to push a test tag to exercise this, or are you handling the first real tag push yourself?
