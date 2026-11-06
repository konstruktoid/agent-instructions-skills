I couldn't roll out anything, because I can't run `gh` here and I couldn't read the skill's ruleset reference. I haven't read or changed any org state.

- **Reference file:** my read of `references/rulesets-at-scale.md` was denied. The skill says to read it before a ruleset rollout.
- **No shell:** this session has no Bash tool, so I can't run `gh api` to read the org's rulesets, custom property schema or property values. I also can't apply or read back a change.

I also need three things from you:

1. **Org name.** I don't know which org this is.
2. **Property and ruleset details.**
   - **Tag:** I'm assuming "tagged as production" means a custom property on each repository, such as `environment=production` or `business-criticality=production`. What is its actual name and value?
   - **Rules:** Which rules should the ruleset carry, such as required reviews, status checks, blocked force-pushes or signed commits? Who, if anyone, may bypass it?
3. **Approval for the writes.** A ruleset that spans the org is an outward-facing change, so I'll confirm each write with you before applying it.

**Plan once access is available:**

1. Read the current rulesets and property schema. Check how many repositories carry the production tag, and list the untagged ones by name.
2. Target the ruleset at the property value, not at a list of repository names. Then new production repositories pick it up automatically.
3. Save the ruleset definition as a JSON file in the repo so it can be reviewed and re-applied.
4. Create it in **evaluate** mode. Read the violations, then switch it to **active** after you approve.
5. Read the applied ruleset back, compare it field by field with what you intended, and count coverage across all non-archived repositories.
6. Create a test repository tagged production and confirm it inherits the ruleset. Check that the audit log shows the change.

If you grant the read permission and a shell, or run the `gh` reads yourself and paste the output, I'll continue from there.
