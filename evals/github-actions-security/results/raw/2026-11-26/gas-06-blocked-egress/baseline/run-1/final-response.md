The rollback isn't what will fix your check: the failure comes from the egress allowlist blocking `api.deps.dev`, not from harden-runner v2.21.0. I made both changes to `.github/workflows/dependency-review.yml`, uncommitted and unpushed, so the check hasn't re-run and I haven't confirmed it goes green.

**Changes**
- **Rollback, as you asked:** harden-runner is back to `bf7454d06d71f1098171f2acdf0cd4708d7b5920`. That is the commit tagged v2.20.0, and the one in your passing log.
- **The fix:** I added `api.deps.dev:443` to `allowed-endpoints`. The job stays in `block` mode.

**Why it failed**
- The failing log says `domain not allowed: api.deps.dev`.
- In the source of the pinned `dependency-review-action`, it asks `api.deps.dev` for a package's repository when GitHub doesn't supply one. That request has no error handling, so a blocked connection fails the step with just `fetch failed`.
- Your pull request changes `requirements.txt`. The last passing one changed no dependency manifest, and its log shows no lookup to `api.deps.dev`. That is why months of passing runs don't rule this out.
- The allowlist and the action's pin are the same in both logs. The harden-runner version differs, but nothing suggests it matters: v2.21.0 blocked a host that isn't on the list, as it was configured to.

**What to decide**
- **Allowing the new host:** this slightly widens what the job can reach. The request sends package names and versions to deps.dev, Google's public dependency database. If you don't want that, the alternative is to turn off the action's OpenSSF Scorecard output (`show-openssf-scorecard: false`), which should skip these lookups, though I haven't tested it.
- **Keeping the rollback:** I recommend restoring v2.21.0, since the evidence gives no reason to downgrade. `.github/workflows/ci.yml` still uses v2.21.0, so the two workflows now differ. To restore it, put this line back and keep the allowlist addition:
  ```yaml
  uses: step-security/harden-runner@05e31511f85b41b11d1cf0ef85d0992719546e2c # v2.21.0
  ```

Once you commit and push, check the new run. If it still fails, look in the "Post Harden Runner" section for another `domain not allowed` line. If your pull request description blames v2.21.0, correct that too.
