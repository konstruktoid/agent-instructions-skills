I can't collect the evidence yet. I was denied permission to read the skill's audit-and-compliance reference file. That file lists which audit log events to collect and how to map them to controls.

I also need three things from you:

1. **Organization name.** I don't know which GitHub org to query, and the audit log endpoints need it (`orgs/ORG/audit-log`).
2. **Credentials.** The audit log needs an organization owner token on a plan that includes audit log access. Please confirm `gh` is authenticated with that. Any read the token can't make will be listed as a gap. I won't present a partial audit as a clean one.
3. **Audit period.** For example, the SOC 2 Type II window the auditor is testing, such as the last 12 months. The REST audit log only goes back a limited time, so older evidence may need to come from your streaming destination.

Once you've granted read access to the reference file and sent the org name, I'll do these things:
- Read the current org state: 2FA, base permissions, rulesets, app and token policy, and audit log streaming and retention.
- Export the audit log events relevant to access changes, permission changes, and policy changes for the period, with pagination.
- Confirm each control has audit entries, and list any control that has none.
- Write the evidence as files in a dedicated directory, with each control's mechanism, evidence and owner. Exceptions will include a reason and an expiry.

All of this is read-only. I won't change any organization settings.
