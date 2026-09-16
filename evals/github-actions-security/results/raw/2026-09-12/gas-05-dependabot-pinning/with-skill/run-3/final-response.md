Verification summary: `actionlint` clean; `zizmor --persona=pedantic` clean at medium/high (one `dependabot-cooldown` finding auto-fixed with a 7-day cooldown; three pre-existing `low`/`help` findings in `ci.yml`/`codeql.yml` — missing `concurrency` blocks and an undocumented `security-events: write` comment — are unrelated to this change and left alone).

One thing to flag on the `github/codeql-action` bump: I pinned it to `v4.38.0`, a major-version jump from the previous `v3`. GitHub currently publishes `v3.x` and `v4.x` in parallel (the split tracks Node runtime requirements, not CodeQL behavior); the changelog shows no functional breaking change at the v3→v4 boundary itself, but confirm your runners are on a CodeQL-compatible image before merging.

Files changed:
- `.github/workflows/ci.yml` — `actions/checkout` and `astral-sh/setup-uv` pinned to SHA with version comments
- `.github/workflows/codeql.yml` — `actions/checkout` and `github/codeql-action/{init,analyze}` pinned to SHA with version comments
- `.github/dependabot.yml` — new: weekly `github-actions` updates grouped into a single PR, 7-day cooldown (zizmor auto-fix)
- `README.md` — explains the SHA-pinning + Dependabot update process

Not committed, per your instructions. `/clear` before starting anything unrelated.
