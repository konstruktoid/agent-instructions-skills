I haven't collected any evidence yet. There's no shell in this session, so I can't run `gh api` against your organization. My attempt to open the skill's audit-and-compliance reference also stopped at a permission prompt that wasn't granted.

To collect it, I need:

1. **Shell access** (Bash) with a `gh` login that has **organization owner** rights. The audit log endpoint is owner-only and needs GitHub Enterprise Cloud.
2. **The organization name** and the **audit period** (SOC 2 Type II usually covers 3–12 months).
3. **Which controls the auditor wants.** If you don't know, I'll cover the usual set below.
4. **Read access** to `references/audit-and-compliance.md` so I can follow its mapping from each control to its evidence.

**What I'd collect, all read-only (`ORG`, `START` and `END` are placeholders):**

```sh
set -euo pipefail
out="$(mktemp -d)"
q='created:START..END'

# Access changes: CC6.2 / CC6.3 (joiners, movers, leavers)
gh api --paginate "orgs/ORG/audit-log?phrase=action:org.add_member+$q&per_page=100" > "$out/org_add_member.json"
gh api --paginate "orgs/ORG/audit-log?phrase=action:org.remove_member+$q&per_page=100" > "$out/org_remove_member.json"
gh api --paginate "orgs/ORG/audit-log?phrase=action:team+$q&per_page=100" > "$out/team.json"
gh api --paginate "orgs/ORG/audit-log?phrase=action:repo.add_member+$q&per_page=100" > "$out/repo_collab.json"

# Authentication controls: CC6.1
gh api --paginate "orgs/ORG/audit-log?phrase=action:org.disable_two_factor_requirement+$q&per_page=100" > "$out/2fa_changes.json"
gh api --paginate "orgs/ORG/audit-log?phrase=action:org_credential_authorization+$q&per_page=100" > "$out/sso_creds.json"

# Change management: CC8.1 (rulesets, branch protection, bypasses)
gh api --paginate "orgs/ORG/audit-log?phrase=action:repository_ruleset+$q&per_page=100" > "$out/rulesets.json"
gh api --paginate "orgs/ORG/audit-log?phrase=action:protected_branch+$q&per_page=100" > "$out/branch_protection.json"

# Privileged / sensitive actions: CC7.2
gh api --paginate "orgs/ORG/audit-log?phrase=action:repo.access+$q&per_page=100" > "$out/visibility.json"
gh api --paginate "orgs/ORG/audit-log?phrase=action:repo.destroy+$q&per_page=100" > "$out/repo_delete.json"
gh api --paginate "orgs/ORG/audit-log?phrase=action:integration_installation+$q&per_page=100" > "$out/app_installs.json"
gh api --paginate "orgs/ORG/audit-log?phrase=action:personal_access_token+$q&per_page=100" > "$out/pat.json"

# Point-in-time configuration snapshot
gh api orgs/ORG > "$out/org_settings.json"
gh api orgs/ORG/audit-log/streams > "$out/streams.json"   # retention / streaming evidence
gh api --paginate "orgs/ORG/rulesets?per_page=100" > "$out/rulesets_now.json"
gh api --paginate "orgs/ORG/members?filter=2fa_disabled&per_page=100" > "$out/2fa_disabled.json"
```

**Two things to settle before relying on this:**

- **Retention.** The audit log UI and API only go back 180 days, and Git events only 7. If your audit period is longer and you aren't streaming to storage you control, the API can't produce the older evidence. The `streams` read above shows whether you are, and that gap would be a finding for the auditor.
- **Packaging.** The output should be a dated folder with a manifest listing each file, its query and time range, the person who ran it, and a SHA-256 hash, so the auditor can trust it wasn't edited. Don't commit it to a repository: audit entries contain real usernames and IP addresses.

If you enable Bash and send me the organization name and period, I'll run the reads and build the manifest. I'll also tell you which reads the token couldn't make, so you don't get a clean-looking result from a partial audit.
