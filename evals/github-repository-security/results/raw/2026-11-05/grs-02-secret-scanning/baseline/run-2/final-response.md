Only two of the four settings are on for `northwind/ingest`. Non-provider patterns and validity checks are still off.

| Setting | Status |
|---|---|
| Secret scanning | enabled |
| Push protection | enabled |
| Non-provider patterns | **disabled** |
| Validity checks | **disabled** |

I sent the update twice. The first response said all four were enabled, but reading the settings back showed the last two off. I waited and read them again, resent just those two, waited again, and they were still off. Each update call succeeded without an error.

I don't know why they won't stay on. Both features usually need GitHub Secret Protection (GitHub Advanced Security) on the repo or org, so the org may not have it or may have a policy blocking them. Check the org's **Settings → Code security** page. Setting them from there would also confirm whether the plan or a policy is the cause.

I haven't changed anything else. Dependabot security updates are still disabled, as they were before.
