An **organization** is where repositories and the people who work on them live. An **enterprise account** sits above one or more organizations and sets policy for all of them centrally.

## Organization

- **What it is:** A shared account that owns repositories, teams, projects, packages and GitHub Apps. It's available on every plan (Free, Team and Enterprise).
- **Who's in it:** Members, outside collaborators and teams. Access is granted per repository through teams and roles (read, triage, write, maintain, admin, plus custom roles on Enterprise).
- **What it controls:**
  - Base permissions for members
  - Whether members can create repositories
  - The two-factor authentication requirement
  - Which actions are allowed and which runners can be used
  - Organization rulesets and custom properties
  - GitHub App and personal access token (PAT) approval
  - Its own audit log
- **Billing:** Each organization is billed separately unless an enterprise owns it.

## Enterprise account

- **What it is:** An account available only on GitHub Enterprise Cloud or Server. It groups several organizations under one company identity. It doesn't hold code directly; repositories still belong to organizations.
- **Who runs it:** Enterprise owners. They don't automatically get access to the code inside each organization, but they set the rules every organization must follow.
- **What it adds:**
  - **Policy enforcement:** It can set policies that organizations can't loosen, such as repository creation, forking, Actions and runner rules, base permissions and 2FA. Each policy can be enforced or left to each organization.
  - **Identity:** SAML or OIDC single sign-on for all organizations at once, plus SCIM provisioning.
  - **Enterprise Managed Users (EMU):** An option where your identity provider creates and owns the user accounts, so they aren't personal GitHub accounts.
  - **Enterprise rulesets and custom properties** that apply across organizations.
  - **Combined audit log** with audit log streaming to a SIEM, and longer retention for Git events.
  - **Shared resources:** Runner groups, GitHub Advanced Security licensing, and one bill with usage reporting across organizations.
  - **Enterprise-only features:** IP allow lists, data residency and similar controls.

## How the policies interact

```
Enterprise  ──(enforced or not)──▶  Organization  ──▶  Repository
```

A setting enforced at the enterprise level is locked in every organization. If the enterprise leaves a setting unenforced, each organization decides it. An organization can generally make a setting stricter than the enterprise default but not looser than an enforced policy.

## Which one you need

- **One team or one product, no central identity requirement:** an organization is usually enough.
- **Several organizations, a central SSO or identity provider, compliance evidence such as SOC 2, PCI or FedRAMP, or a need to stop each organization from relaxing security settings:** use an enterprise account and enforce the policies that matter there.
