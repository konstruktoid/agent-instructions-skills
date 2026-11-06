I couldn't restrict the allowed actions yet, and I haven't changed anything. My attempt to read the skill's `references/policies.md` was denied. That file holds the allowed-actions and runner-policy details the skill says to read before changing this setting.

I also have no shell or `gh` access in this session. That means I can't read your organization's current actions policy or apply a new one.

Here is what I'd do once I have access to the reference file and a way to call the GitHub API. I'd also need an organization-owner token with the `admin:org` scope:

1. **Read the current state.** I'd read `gh api orgs/ORG/actions/permissions` and `orgs/ORG/actions/permissions/workflow`. I'd also check whether an enterprise policy already limits what the organization can set.
2. **Propose the policy.** This is what I'd propose, subject to what `policies.md` says:
   - Set `allowed_actions` to `selected`.
   - Allow GitHub-owned actions and verified creators only if you want them.
   - Add an explicit allowlist of `owner/repo@ref` patterns, pinned to full commit SHAs where possible.
   - Set the default workflow token to read-only, and block workflows from approving pull requests.
3. **Get your approval before applying.** Changing organization-wide actions policy affects every repository, so I'd show you the exact allowlist first. A tighter policy can break existing workflows.
4. **Check what would break.** I'd scan the actions your repositories currently use, so the allowlist doesn't stop working pipelines.
5. **Read it back.** I'd read each setting again in a separate request and compare it with what I intended. I'd also confirm the change shows up in the audit log, and keep the policy in a committed file so it can be reviewed and reapplied after drift.

To proceed, I need three things from you:
- Permission to read the `references/policies.md` file.
- A way to run `gh` commands, or confirmation that I should only draft the commands and policy file for you to run.
- The organization name, and which actions you want allowed. For example, GitHub-owned only, or GitHub-owned plus specific third-party actions.
