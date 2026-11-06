Secret scanning and push protection are now on for northwind/ingest. Validity checks and non-provider patterns are still off, so the request is only partly done.

I changed all four settings in one update. Then I re-read the repository in a separate request to check what was applied:

| Setting | Before | After |
|---|---|---|
| `secret_scanning` | disabled | **enabled** |
| `secret_scanning_push_protection` | disabled | **enabled** |
| `secret_scanning_validity_checks` | disabled | still **disabled** |
| `secret_scanning_non_provider_patterns` | disabled | still **disabled** |

The API accepted the update without an error, but it did not apply those last two fields. I did not retry. Retrying an ignored field won't change the result.

**What you need to do:** turn on validity checks and non-provider patterns in the web interface. Go to Settings → Advanced Security (or Code security) for the repository. They may also depend on a plan or an organization-level setting that I can't see from here. Check the organization's code security configuration, because an organization policy can override repository settings.

I can re-read the settings after you've changed them. I haven't tested push protection by pushing a test secret, so it is unverified. A push containing a known-format token is the event that would exercise it.

If a secret is ever found, rotate or revoke it first, before cleaning history.

I made no repository file changes and no commits.
