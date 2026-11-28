I haven't changed anything yet. This session has no shell, so I can't run `gh` against your org, and my request to read the skill's `rulesets-at-scale.md` reference wasn't approved. Below is the rollout plan. Every write in it needs your approval first, because an organization ruleset applies to all your production repositories at once.

## What I need from you

1. **Organization name.**
2. **How "production" is tagged.** I'm assuming a custom property, such as `environment` or `business-criticality` set to `production`. If it's a GitHub topic or a naming convention, we should turn it into a custom property first. Otherwise any new production repository would be left out.
3. **What the ruleset should enforce.** For example: required pull request reviews, required status checks, no force pushes, no deletions, signed commits. Also say which branches it covers (default branch only, or `release/*` too).
4. **Bypass actors, if any.** Each one is an exception and needs a reason and an expiry.

## Plan

**1. Read the current state (no writes)**
```sh
gh api orgs/ORG/properties/schema --jq '.[] | {property_name, value_type, allowed_values}'
gh api --paginate "orgs/ORG/rulesets?per_page=100" --jq '.[] | {id, name, enforcement}'
```

**2. Check that every production repository is tagged.** These commands list active repositories with no value for the property. Those are the ones the ruleset would miss.
```sh
set -euo pipefail
d="$(mktemp -d)"
gh api --paginate orgs/ORG/repos --jq '.[] | select(.archived==false) | .name' | sort > "$d/all"
gh api --paginate orgs/ORG/properties/values --jq '.[] |
  select(any(.properties[]; .property_name=="environment" and .value!=null)) |
  .repository_name' | sort > "$d/tagged"
comm -23 "$d/all" "$d/tagged"
```
Fix any gaps before enforcing. Making the property required with a default value means new repositories can't skip it.

**3. Commit the ruleset definition to a file, for example `rulesets/production.json`.** It targets the property, not a list of repository names, so production repositories created later are covered automatically:
```json
{
  "name": "production-baseline",
  "target": "branch",
  "enforcement": "evaluate",
  "conditions": {
    "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] },
    "repository_property": {
      "include": [{ "name": "environment", "property_values": ["production"] }],
      "exclude": []
    }
  },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    { "type": "pull_request", "parameters": {
        "required_approving_review_count": 1,
        "dismiss_stale_reviews_on_push": true,
        "require_code_owner_review": true,
        "require_last_push_approval": true,
        "required_review_thread_resolution": true } }
  ],
  "bypass_actors": []
}
```

**4. Apply it in evaluate mode (needs your approval):**
`gh api -X POST orgs/ORG/rulesets --input rulesets/production.json`

**5. Watch the rule insights for about a week.** Find which rule fires most and fix the repositories or the rule before blocking anyone.

**6. Switch to active (needs separate approval).** Change `enforcement` to `active` in the file and run `PUT orgs/ORG/rulesets/ID`.

**7. Verify:**
- Read the ruleset back with `GET orgs/ORG/rulesets/ID` and compare it to the file field by field.
- Re-run the step 2 coverage check and list any missed repositories by name.
- Confirm the change appears as a `repository_ruleset.create` or `.update` event in the audit log.
- Confirm a newly created production repository picks up the ruleset without anyone configuring it.

Send me the four answers above and I'll finalize the JSON. To have me run the commands, you'd need to give me shell access with a `gh` token from an organization owner. Otherwise you can run them and paste the output back to me.
