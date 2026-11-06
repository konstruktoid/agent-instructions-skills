Secret scanning and push protection are now on for `northwind/ingest`. Validity checks and the non-provider patterns are still off, so the request is only partly done. I read the settings back with a separate request, and these are the values it returned:

| Setting | Before | After |
|---|---|---|
| `secret_scanning` | disabled | **enabled** |
| `secret_scanning_push_protection` | disabled | **enabled** |
| `secret_scanning_validity_checks` | disabled | **disabled** |
| `secret_scanning_non_provider_patterns` | disabled | **disabled** |

I sent all four settings in one update. The update response showed secret scanning and push protection as enabled, but the read-back showed the other two unchanged. I did not retry. A setting the API accepts but doesn't apply isn't something a retry fixes. I don't know the cause. I did not check the organization's security configuration or the repository's plan.

**What you need to do:** turn on validity checks and non-provider patterns in the web interface, under Settings → Advanced Security (Code security) for the repository. If the organization manages these through a code security configuration, they may need to be switched on there. Once that's done I can read the state back again.

**Not checked:**
- **Push protection:** I haven't tested it with a push containing a test secret, so it is unverified. A blocked push of a known test token would show it working.
- **Existing secrets:** Scanning of existing history will produce alerts over time. If any alert shows up, rotate the credential first, before touching history.
