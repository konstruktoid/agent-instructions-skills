**Files changed:** `.github/workflows/ci.yml`, `README.md`.

Verification: `actionlint` clean (exit 0). `zizmor --persona=pedantic` down from 7 findings (2 high, 1 low) to 1 informational finding (exit 11), documented as a deliberate exception in a comment on the `npm publish` line — the task specifies NPM_TOKEN, not trusted publishing.

This is structural verification only — I did not push the branch or trigger the workflow on GitHub, so the tag-push path and npm publish/release creation are unverified in a live run. Say if you want me to push a test tag to exercise it.

One deviation from repo convention worth flagging: the existing workflow pinned actions by tag (`@v4`); I re-pinned both to commit SHA per the security skill's baseline, which overrides that convention per this session's CLAUDE.md precedence rule (repo convention loses to the skill's explicit "pin every third-party action to a full commit SHA" requirement).
