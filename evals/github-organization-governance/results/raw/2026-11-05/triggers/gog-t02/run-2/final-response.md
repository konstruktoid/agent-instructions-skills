I can't roll the ruleset out yet. I tried to read the skill's ruleset reference file, `references/rulesets-at-scale.md`, and the read was denied. I haven't run any `gh` commands, and I haven't changed anything in your org.

Before I continue, I need two things from you:

1. **Access to the reference file.** Please grant read access to the plugin directory, or paste the file's contents. The skill says to read it before changing any rulesets.
2. **Three details about the rollout:**
   - **Org name:** which org should this go to?
   - **Production tag:** which custom property marks a repository as production, and what is its value? For example, `environment=production` or `criticality=high`. I'll read the property schema first to check that it exists and is populated.
   - **Ruleset rules:** which rules should it contain? For example, required PR reviews, blocked force-pushes, required status checks. Do you have a definition file already?

Once I have those, I plan to work in this order:

1. **Read the current state.** I'll read the existing rulesets and the property schema.
2. **Measure property coverage.** Any repository that should be tagged production but isn't would be missed, so I'll list those by name.
3. **Write the ruleset as a committed file.** It will target the property, not a list of repository names, so new production repositories pick it up automatically.
4. **Create it in evaluate mode.** This needs your approval, because the ruleset spans the whole org.
5. **Review the violations, then switch it to active.** Switching also needs your approval.
6. **Read the settings back and measure coverage.** I'll check that every production repository is covered.
