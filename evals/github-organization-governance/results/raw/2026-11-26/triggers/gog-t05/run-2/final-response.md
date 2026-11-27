I couldn't collect any evidence yet. I have no shell in this session, so I can't run `gh api` against your organization. My request to read the skill's audit-and-compliance reference was also declined, so I haven't seen that file's guidance. No audit log data has been read, and nothing has been changed in your organization.

To run the collection, I need:

1. **The organization name**, and whether it sits under an enterprise.
2. **The audit period** the auditor asked for (for example 2025-12-01 to 2026-11-30). GitHub only keeps searchable audit log events for a limited time (about 180 days for most events, less for Git events), so the start of a full year may already be gone unless you stream the log elsewhere.
3. **Whether you stream the audit log** to storage you control (S3, Azure, Splunk, Datadog and so on). If you do, the full-period evidence should come from there and GitHub only adds to it.
4. **Credentials:** an organization owner token with `read:audit_log`, on a plan that includes the audit log API (Enterprise Cloud).
5. **Shell access** in this session, or you can run the commands below and give me the output files.

## Commands to run (replace `ORG`, `FROM`, `TO`)

```sh
set -euo pipefail
out="soc2-evidence-$(date +%F)"; mkdir -p "$out"

# Point-in-time configuration (for control design)
gh api orgs/ORG > "$out/org-settings.json"
gh api orgs/ORG/actions/permissions > "$out/actions-permissions.json"
gh api orgs/ORG/actions/permissions/workflow > "$out/workflow-token.json"
gh api --paginate "orgs/ORG/rulesets?per_page=100" > "$out/rulesets.json"
gh api --paginate "orgs/ORG/members?filter=2fa_disabled&per_page=100" > "$out/members-2fa-disabled.json"
gh api --paginate "orgs/ORG/outside_collaborators?per_page=100" > "$out/outside-collaborators.json"
gh api --paginate "orgs/ORG/installations?per_page=100" > "$out/app-installations.json"
gh api orgs/ORG/audit-log/streams > "$out/audit-streams.json" || echo "streaming read failed" >&2

# Audit log events over the period (for operating effectiveness)
for q in \
  "action:org.add_member" "action:org.remove_member" "action:org.update_member" \
  "action:team.add_member" "action:team.remove_member" \
  "action:org.add_outside_collaborator" "action:repo.add_member" \
  "action:org.update_default_repository_permission" \
  "action:org.disable_two_factor_requirement" "action:org.enable_two_factor_requirement" \
  "action:org.saml_disabled" "action:org.saml_enabled" \
  "action:repository_ruleset" "action:protected_branch" \
  "action:repo.access" "action:repo.destroy" "action:repo.transfer" \
  "action:integration_installation" "action:personal_access_token" \
  "action:org.audit_log_stream"; do
  f="$out/audit-$(echo "$q" | tr ':.' '__').json"
  gh api --paginate \
    "orgs/ORG/audit-log?phrase=$(printf '%s' "$q created:FROM..TO" | jq -sRr @uri)&per_page=100&include=all" \
    > "$f"
done
sha256sum "$out"/* > "$out/SHA256SUMS"
```

These event queries line up with the SOC 2 criteria auditors usually test:

- **CC6.1 / CC6.2 / CC6.3:** granting and removing access, team membership, collaborators, and base permission.
- **CC6.1:** two-factor and SAML enforcement, and tokens and apps.
- **CC8.1:** change management through rulesets and branch protection.
- **CC7.2:** monitoring, through audit log streaming.

The checksums file shows the exported evidence hasn't been altered since it was pulled.

## Gaps to report, not hide

- **An empty file means no event was found, not that the control worked.** The auditor needs the sample tied to tickets, for example a `remove_member` matched to an HR termination.
- **Retention:** if the period starts before what GitHub still keeps and there's no stream, report the missing months instead of passing off a partial log as complete.
- **Authorization errors:** any read that fails with 403/404 should be named in the evidence package as not collected.

Send me the organization name and period, and either turn on shell access or give me the output. I'll then map each file to its SOC 2 criterion, flag gaps such as members without two-factor, outside collaborators with no expiry, or missing streaming, and draft the evidence index for the auditor.
