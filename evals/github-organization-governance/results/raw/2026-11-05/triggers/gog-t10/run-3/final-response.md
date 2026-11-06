# GitHub organization vs. enterprise account

**Organization**
- A shared account where people collaborate across many repositories.
- It's the unit where you manage members, teams, and repository access.
- Settings you control include:
  - base permissions and member privileges
  - teams and roles
  - 2FA requirements
  - rulesets
  - Actions policies
  - GitHub App and token policies
  - the audit log
- Each organization is configured on its own. SAML SSO at the organization level requires GitHub Enterprise Cloud.

**Enterprise account**
- A layer above organizations, available with GitHub Enterprise (Cloud or Server).
- It doesn't hold repositories itself. It groups multiple organizations under one umbrella for central governance and billing.
- It lets you:
  - set policies that apply to all organizations, or set defaults that organizations can't override
  - manage billing, licenses, and spending in one place
  - configure identity centrally, such as SAML SSO, SCIM, and Enterprise Managed Users (EMU)
  - use enterprise-wide audit log streaming and retention
  - define enterprise-level roles, such as enterprise owners, and custom repository roles or rulesets (depending on plan)
  - manage self-hosted runners and runner groups across organizations

| | Organization | Enterprise account |
|---|---|---|
| Holds repositories | Yes | No (its organizations do) |
| Scope | One group or company unit | Many organizations |
| Main purpose | Collaboration and access control | Central policy, identity, billing |
| Policy control | Per organization | Can enforce across all organizations |
| Plan | Free, Team, or Enterprise | Enterprise only |

**Rule of thumb:** use organizations to run teams and repositories. Use an enterprise account when you need consistent policy, single sign-on, auditing, and billing across several organizations.

I can go deeper on any of these, such as which policies are enforced from the enterprise level versus the organization level.
