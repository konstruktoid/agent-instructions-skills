Done. Summary:

**Files changed:**
- `.github/dependabot.yml` (new) — `github-actions` ecosystem, weekly schedule, 7-day cooldown, all updates grouped into a single PR via `groups: github-actions: patterns: ["*"]`.
- `.github/workflows/ci.yml`, `.github/workflows/codeql.yml` — replaced mutable major-version tags (`@v5`, `@v6`, `@v3`) with full commit SHAs and a trailing version comment, so Dependabot has SHAs to rewrite and comments to update:
  - `actions/checkout` → `v7.0.1` (`3d3c42e...`)
  - `astral-sh/setup-uv` → `v10.0.1` (`20cfd1b...`, not `v10.1.0` — that release is 3 days old, inside the 7-day cooldown just configured)
  - `github/codeql-action/{init,analyze}` → `v4.37.9` (`cdf488f...`, not `v4.38.0` for the same cooldown reason)
- `README.md` — added a section explaining the pin-by-SHA + Dependabot-review workflow.

**Note on the codeql-action major bump (v3→v4):** the only breaking change is that the action now requires Node.js 24 at runtime; `ubuntu-latest` already provides this, so no workflow change was needed beyond the pin.

**Verification:** `actionlint` clean. `zizmor --persona=pedantic` went from 9 findings (6 high — unpinned actions) to 3 low findings, all pre-existing and outside this task's scope: missing `concurrency:` blocks on both workflows, and an undocumented-comment nit on the `security-events: write` permission in `codeql.yml`. I stopped there rather than expanding scope — let me know if you want those addressed too.

No commits were made. You can `/clear` before starting anything unrelated.
