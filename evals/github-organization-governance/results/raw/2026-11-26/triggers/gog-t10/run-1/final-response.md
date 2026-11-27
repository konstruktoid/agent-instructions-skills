A GitHub **organization** is a shared account where people and teams work on repositories together. An **enterprise account** sits one level higher. It groups several organizations under one owner, so policy, identity and billing can be managed in one place.

## Organization
- **What it holds:** Repositories, teams, projects, packages, GitHub Apps and Actions settings.
- **Who's in it:** Members and outside collaborators. Access is granted by role: owner, member, billing manager, security manager, or custom roles on Enterprise Cloud.
- **Policy scope:** Applies only to that organization. Examples: base repository permissions, 2FA requirement, allowed actions, organization rulesets, custom properties, and approval of personal access tokens and apps.
- **Plans:** Free, Team or Enterprise Cloud. A standalone organization can use Enterprise Cloud without an enterprise account, though most Enterprise Cloud customers now get one.

## Enterprise account
- **What it holds:** Organizations, not repositories. It's a management layer above them.
- **Who's in it:** Enterprise owners and billing managers, plus every member of its organizations, who count as enterprise members for licensing.
- **Policy scope:** Applies to every organization it contains. An enterprise policy can either **enforce** a setting, which org owners can't override, or **leave it to each organization**. Examples: repository creation and forking rules, Actions and runner policy, 2FA, enterprise-wide rulesets and custom properties, and Copilot.
- **Identity:**
  - SAML or OIDC single sign-on can be set once for every organization.
  - Enterprise Managed Users (EMU) goes further. Your identity provider creates and controls the user accounts, which are scoped to the enterprise and can't work on public github.com content.
- **Billing and licensing:** One bill and one license count across all organizations. Each user is counted once, even if they belong to several organizations.
- **Audit and compliance:** An enterprise audit log covering all organizations, audit log streaming to a SIEM, and compliance reports.
- **Deployment:** Available on GitHub Enterprise Cloud, including the data residency option on GHE.com. GitHub Enterprise Server effectively has one enterprise per instance.

## How they fit together
```
Enterprise account   ← identity, enforced policy, billing, audit
 ├── Organization A  ← teams, repos, org-level settings
 ├── Organization B
 └── Organization C
```

**Rule of thumb:** If you have one team or product, one organization is usually enough. Use an enterprise account when several organizations need the same security baseline, shared SSO, combined billing or central audit, or when you need EMU.

If you're deciding how to structure or harden your own setup, I can help with that next, for example which settings to enforce at enterprise level and which to leave to each organization.
