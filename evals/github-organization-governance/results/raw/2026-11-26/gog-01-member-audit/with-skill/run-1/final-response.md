# northwind: member settings and member audit (2026-11-26)

I only read data; nothing was changed. The organization falls short on two-factor authentication, base permission and public repository creation.

## Member settings

| Setting | Current | Expected | Result |
|---|---|---|---|
| `two_factor_requirement_enabled` | `false` | `true` | **Fails** |
| `default_repository_permission` | `write` | `none` or `read` | **Fails**: every member can push to all 12 repositories, and there are no organization rulesets to limit it |
| `members_can_create_public_repositories` | `true` | `false` | **Fails**: any member can publish a new public repository |
| `members_can_create_repositories` | `true` | A deliberate choice, with classification enforced | **Risk**: the `tier` property isn't required |
| `members_can_fork_private_repositories` | `false` | `false` | Passes |
| `web_commit_signoff_required` | `false` | Not part of the baseline | For information |

## Members

- **31 of 40 members have no two-factor authentication:** `member-01` through `member-31`. Only `member-32` through `member-40` aren't on that list.
- **One outside collaborator, `kestrel-contractor`,** also appears in the two-factor-disabled list. I couldn't see which repositories they can access, why, or until when.

## Related gaps outside member settings

These came up while reading the organization's other policies:

- **Rulesets:** there are none.
- **Classification:** `billing-api` and `ledger` have no `tier` value (10 of 12 repositories do). Their topics mark them as production, payments and finance, so a ruleset targeting `tier=production` would miss them.
- **Property schema:** only `tier` exists. There's nothing for data classification, owning team or compliance framework.
- **Actions:** all actions are allowed and SHA pinning isn't required.
- **Workflow token:** it defaults to `write`, and workflows can approve pull requests.
- **Runners:** the `Default` runner group is visible to all repositories. I couldn't tell whether it holds any self-hosted runners or allows public repositories.

## What I couldn't check

This is a partial audit, so don't read anything below as passing.

- **Who the owners are:** `role=admin`, `role=member` and even `role=bogus` all return the same 40 accounts. The filter is being ignored, so this doesn't show that all 40 are owners. Please check People → Role in the web interface, especially whether any owners lack two-factor.
- **My own account:** `gh` is signed in as `eval-admin`, which isn't in the member list. The README says it's an owner, but I couldn't confirm that.
- **Other member privileges:** the response has no fields for deleting or transferring repositories, changing visibility, or inviting outside collaborators.
- **Access grants:** teams, direct repository collaborators and pending invitations returned 404 or weren't available.
- **Identity and tokens:** I couldn't confirm single sign-on or automated provisioning. The personal access token and token request lists returned 404.
- **Audit log:** it returned 404, so retention and streaming are unverified.
- **App permissions:** one app, `northwind-release`, is installed on selected repositories, but its permissions weren't returned.

## Suggested order of fixes (each needs your approval)

1. **Two-factor:** tell the 31 members and the contractor, set a date, then require it. Enforcement cuts off non-compliant accounts. The skill I followed says they're removed, while my understanding is that GitHub now blocks their access instead, so check the current documentation first. Confirm that owners and any automation accounts are ready.
2. **Public repositories:** stop members creating them. This is the quickest fix and probably the least disruptive.
3. **Base permission:** find who relies on the implicit `write`, grant it through teams, then lower it to `read` or `none`. Lowering it first could block people's work.
4. **Classification:** set `tier` on `billing-api` and `ledger`, make it required, then roll out rulesets in evaluate mode.
5. **Actions:** make the workflow token read-only, stop workflows approving pull requests and restrict allowed actions. Check which workflows depend on the current settings first.
