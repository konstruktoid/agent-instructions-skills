I can't proceed with the rollout yet. Reading the ruleset reference file was denied, and I don't want to start without it.

The skill says to read `references/rulesets-at-scale.md` before any ruleset rollout. It covers property schemas, tiering, targeting, and staged rollout. I tried to read it and the permission was denied. Please either grant read access to that path or paste its contents.

I also need these from you before changing anything:

1. **Org name**, and confirmation that `gh` is authenticated with an org-owner token.
2. **The custom property that marks production.** I need its name and value, for example `environment=production` or `business-criticality=high`. I'll check the schema and its coverage first. A ruleset that targets a property only works if every production repo carries it, and repos missing it would be skipped without any warning.
3. **The rules to include**, such as PR review, required status checks, blocking force-push and deletion, or signed commits. I also need any bypass actors. Adding a bypass actor is a proposal that needs your approval.

When I have those, I'll follow this order:
1. Read the current state: existing rulesets, the property schema, and which repos have no value for the property.
2. Write the ruleset definition to a committed file so it can be reviewed and diffed.
3. Create it in **evaluate** mode and read the reported violations.
4. Ask you to confirm before I switch it to **active**.
5. Read each setting back and list any repos the ruleset misses by name.

I won't create or enable anything until you confirm.
