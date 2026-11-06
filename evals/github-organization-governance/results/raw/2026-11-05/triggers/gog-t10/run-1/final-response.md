# GitHub organization vs. enterprise account

**Organization**
- A shared account that groups people and repositories under one owner, such as a company, team, or open-source project.
- It manages members, teams, repository permissions, and base permissions.
- It sets policy for its own repositories. That includes 2FA requirements, SSO (SAML) on Enterprise Cloud, allowed Actions, rulesets, GitHub App and token policy, and audit log access.
- Billing and plan (Free, Team, or Enterprise) apply per organization unless an enterprise account sits above it.
- Its scope is a single organization. Policies don't carry over to other organizations.

**Enterprise account**
- A layer **above** organizations. It lets you manage multiple organizations together.
- It provides centralized billing, licensing, and a single place to view consumption across organizations.
- It applies policies across all organizations, or sets defaults they can't override. Examples are repository creation, forking, Actions, and Copilot.
- It has an enterprise-level audit log, with streaming and API access across organizations.
- It handles identity centrally with SAML SSO and SCIM, or with Enterprise Managed Users (EMU), where the IdP controls the user accounts.
- It has enterprise owners, who sit above organization owners, and it supports enterprise-wide roles and teams.
- It requires a GitHub Enterprise plan.

**Key differences**

| | Organization | Enterprise account |
|---|---|---|
| Contains | Repos, teams, members | Organizations |
| Policy scope | One organization | All organizations in the enterprise |
| Billing | Per organization | Consolidated |
| Identity | Org-level SSO and 2FA | Central SSO, SCIM, EMU |
| Audit log | Per organization | Enterprise-wide |
| Admin role | Organization owner | Enterprise owner |

**Rule of thumb:** use a single organization when one group of people and repositories is enough. Add an enterprise account when you have several organizations and need one place for billing, identity, policy, and auditing.

I can also go into how policy inheritance works, with enterprise policy vs. organization override, or how to audit and harden either level.
