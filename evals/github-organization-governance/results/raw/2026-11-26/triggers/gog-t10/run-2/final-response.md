A **GitHub organization** is a shared account where people work together on a set of repositories. An **enterprise account** sits above one or more organizations and controls them from one place.

## Organization

- **Scope:** It owns repositories, teams, projects, packages and GitHub Apps.
- **Who's in it:** Members and outside collaborators. Access is given through base permissions, teams and repository roles.
- **What you can set:** Member privileges, a two-factor requirement, rulesets, custom properties, the allowed-actions policy, runners, app and token policy, and the audit log. All of these apply only to that one organization.
- **Plans:** Free, Team or Enterprise Cloud. An organization can exist without an enterprise.
- **Billing:** Each organization is billed separately unless it belongs to an enterprise.

## Enterprise account

- **Scope:** It contains organizations, not repositories directly (except personal repositories under Enterprise Managed Users).
- **Policy:** Enterprise policies apply to every organization inside it. A policy can either be enforced, so organizations can't change it, or left as "no policy", so each organization decides. Examples include base permissions, repository creation and visibility, forking, Actions and runners, two-factor, and personal access tokens.
- **Identity:** It can set up SAML or OIDC single sign-on for every organization at once. It can also use **Enterprise Managed Users (EMU)**, where your identity provider creates and controls the accounts. Those accounts can't contribute outside the enterprise.
- **Governance:**
  - An enterprise-wide audit log and audit log streaming
  - Enterprise rulesets and custom properties
  - Shared runner groups
  - Licence management based on unique users, so a person in five organizations uses one seat
- **Billing:** All organizations share one bill, with GitHub Advanced Security, Copilot and Actions usage combined.
- **Deployment:** It's needed for GitHub Enterprise Cloud (including data residency on GHE.com) and is the model GitHub Enterprise Server uses.

## Main differences

| | Organization | Enterprise |
|---|---|---|
| Contains | Repositories and teams | Organizations |
| Policy reach | One organization | Every organization, and can lock settings |
| Single sign-on | Per organization | Enterprise-wide, plus the EMU option |
| Audit log | Organization events | All organizations combined, with streaming |
| Billing and seats | Per organization | One bill, unique-user licensing |

**When you need an enterprise:** If you have a single team, one organization is usually enough. Once you have several organizations, compliance needs (central audit, enforced single sign-on or EMU, policies teams can't change), or a need for one combined bill, set up an enterprise. Put the guardrails at the enterprise level and leave the day-to-day choices to each organization.
