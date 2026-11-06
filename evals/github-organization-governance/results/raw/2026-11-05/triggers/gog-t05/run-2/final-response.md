I can't start collecting evidence yet, for two reasons.

1. **I can't read the skill's reference files.** Permission to read `references/audit-and-compliance.md` and `instructions/github_governance_instructions.md` was denied. The skill says to read the audit reference before assembling SOC 2 evidence, and I don't want to work from memory. If you grant read access to the plugin directory, I'll continue.

2. **I need the organization name.** The audit log reads use `gh api orgs/ORG/...`, and nothing in this workspace names the organization. Please confirm two things:
   - **Organization slug:** which organization to collect from.
   - **Credentials:** whether `gh` is authenticated as an organization owner. The audit log (`orgs/ORG/audit-log`) needs an owner token and a plan that includes audit log access. If a read fails, I'll report which one failed. I won't report a clean result from a partial audit.

Once I have both, this is what I plan to collect. Every step is read-only, and nothing is changed.
- **Audit log events:** a paginated export for the audit period, covering the events auditors usually ask about. Those are membership and role changes, permission changes, repository visibility, deletion and transfer, ruleset and branch protection changes, app installs, token and SSO events, and runner and Actions policy changes.
- **Configuration snapshot:** org settings (2FA, base permission, repository creation), rulesets, custom property coverage, Actions and runner policy, app installations, members without 2FA, and outside collaborators.
- **Streaming and retention:** whether audit log streaming is configured, and what the retention period is.
- **Evidence package:** each control recorded with its mechanism, evidence, and owner. Any gaps or reads I couldn't make are listed.

Two questions on scope:
- **Audit period:** what dates does the auditor need? SOC 2 Type II typically covers 6 to 12 months. GitHub keeps audit log events for only about 180 days through the API, so streaming may be the only source for older events.
- **Output location:** where should I write the evidence files? I'd suggest a new directory outside the repo so that no usernames or tokens end up committed.
