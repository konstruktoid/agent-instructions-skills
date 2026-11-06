# GitHub organization vs. enterprise account

**Organization**
- It's a shared account that groups people and repositories. It's the main unit for day-to-day collaboration.
- Members get roles (owner, member, and so on), and you organize them into teams.
- Repository access comes from base permissions, team membership, and per-repo roles.
- Settings apply to that one organization. These include member privileges, 2FA requirement, allowed Actions, GitHub App and token policy, rulesets, and the audit log.
- SAML SSO is available on Enterprise Cloud, configured per organization.

**Enterprise account**
- It sits above organizations and lets you manage many of them together. Its main purpose is central governance, billing, and policy.
- It needs GitHub Enterprise Cloud (or Enterprise Server, which has a similar concept).
- It has no repositories of its own. Repositories always live in organizations.
- Enterprise owners can:
  - Enforce policies across all organizations, or let each organization choose. Examples are repository creation, forking, Actions, and 2FA.
  - Bill centrally, with one license pool and shared usage for Actions minutes, Packages, and Codespaces.
  - Manage identity centrally, with enterprise-wide SAML SSO and SCIM, or Enterprise Managed Users (EMU), where the IdP controls the accounts.
  - View the enterprise audit log, stream it, and set enterprise-level security and compliance settings.
  - Create and manage organizations, and set enterprise-level roles such as the enterprise owner and billing manager.

**Key differences**

| | Organization | Enterprise account |
|---|---|---|
| Contains | Repos, teams, members | Organizations |
| Scope of policy | One org | All orgs in the enterprise |
| Billing | Per org (or via enterprise) | Centralized |
| Identity/SSO | Per org | Enterprise-wide, plus EMU option |
| Typical use | Team collaboration | Governance, compliance, cost control |

**Rule of thumb:** use an organization to manage who works on which code. Use an enterprise account to set consistent policy, identity, and billing across several organizations. A single small team usually only needs an organization.

I can go further on any of these, such as EMU vs. regular accounts or which policies can be enforced at the enterprise level.
