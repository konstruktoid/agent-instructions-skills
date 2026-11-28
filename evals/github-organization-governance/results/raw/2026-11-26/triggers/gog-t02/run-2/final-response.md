I haven't changed anything yet. I can't make that change from this session: I have no shell, so I can't run `gh api` against your org. I also wasn't allowed to read the skill's `rulesets-at-scale.md` reference file. And an org-wide ruleset is the kind of fleet-wide change I'd need your go-ahead for anyway. Here's the plan and a draft definition to review.

## What I need from you

1. **The org name**, and a token with org owner (or ruleset admin) rights.
2. **What "tagged as production" means.** Is it a custom property (for example `environment = production`), or a repository topic? A ruleset can target a custom property directly, and that's the approach I recommend. A topic can't be targeted. If it's a topic, the first step is to create a property and fill it in from the topics.
3. **Which rules the ruleset should enforce.** My draft below is a reasonable production default.
4. **Bypass actors, if any.** Each one is a separate approval and needs a reason and an expiry.

## Rollout plan

1. **Read the current state:** existing rulesets, the property schema, and which repos have the property set. Every list is read with `--paginate`, so the full fleet is counted, not just the first page.
   ```sh
   gh api --paginate "orgs/ORG/rulesets?per_page=100" --jq '.[] | {id,name,target,enforcement}'
   gh api orgs/ORG/properties/schema --jq '.[] | {property_name,value_type,allowed_values}'
   ```
2. **Fill in the property first.** Find the repos that aren't classified yet and list them by name. Any repo missing the property won't be covered by the ruleset, even if it really is production.
3. **Create the ruleset in evaluate mode** from a committed file (draft below): `gh api -X POST orgs/ORG/rulesets --input rulesets/production.json`
4. **Review the violations** in rule insights for a reasonable period, note which rule fires most, and fix the cause or adjust the rule.
5. **Switch to `active`** only after you approve that step separately.
6. **Verify:**
   - Read the ruleset back and compare it field by field.
   - Count the production repos it covers against the ones it misses.
   - Confirm the audit log has the `repository_ruleset.create`/`update` events.
   - Check that a newly created repo with the property is covered automatically.

## Draft `rulesets/production.json`

```json
{
  "name": "production-baseline",
  "target": "branch",
  "enforcement": "evaluate",
  "conditions": {
    "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] },
    "repository_property": {
      "include": [{ "name": "environment", "property_values": ["production"], "source": "custom" }],
      "exclude": []
    }
  },
  "bypass_actors": [],
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    { "type": "required_linear_history" },
    { "type": "required_signatures" },
    { "type": "pull_request", "parameters": {
        "required_approving_review_count": 1,
        "dismiss_stale_reviews_on_push": true,
        "require_code_owner_review": true,
        "require_last_push_approval": true,
        "required_review_thread_resolution": true
    } }
  ]
}
```

If your property name or value is different, change `environment` and `production` to match.

Send me the org name and your answers to questions 2 to 4. If you can also give me shell access, or run the read commands above and paste the output, I'll finish the property coverage check before anything is created.
