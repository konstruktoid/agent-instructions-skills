I haven't changed anything yet. I can't run `gh` in this session, and my request to read the skill's ruleset rollout guide (`references/rulesets-at-scale.md`) wasn't approved. A ruleset across every production repo is a fleet-wide change, so I need a few answers and your go-ahead before I apply it.

**What I need from you**

1. **The organization name**, and whether you're an org owner or have a token with org admin rights. Rulesets, custom properties and the coverage check all need that.
2. **What "tagged as production" means for you:**
   - A **custom property** (for example `environment=production`). The ruleset can target this directly, and repos tagged later are picked up automatically.
   - A **repository topic** (the `production` tag on a repo page). Rulesets can't target topics. I'd create a custom property, copy the topic onto it for every repo that has it, and target the property. A ruleset aimed at a fixed list of repo names goes stale as soon as someone creates a new repo.
3. **Which rules it should contain.** You might have an existing ruleset JSON file, or want me to copy one from a repo or the org. Otherwise I'd propose:
   - Rules for the default branch:
     - Changes go through a pull request with at least 1 approving review.
     - Approvals are dismissed when new commits are pushed.
     - Code owners must review.
     - Status checks must pass.
     - Force pushes and branch deletion are blocked.
   - **Bypass actors:** none, or only a named team. Every bypass actor is an exception you should approve explicitly.

**How I'd roll it out once you answer**

1. **Read the current state:**
   - The org's existing rulesets, so the new one doesn't overlap or conflict with them.
   - The custom property setup.
   - Which repos actually carry the production tag.

   All of these lists span several pages, so I'll fetch every page rather than just the first.
2. **Fill in the property** on any production repo that's missing it. I'll show you the list first and wait for your go-ahead.
3. **Keep the ruleset in a file committed to a repo**, so you can review and diff it.
4. **Create it in evaluate mode** so it reports violations without blocking anyone. Then I'll show you which rules fire most and on which repos.
5. **Switch it to active** after you approve. That's a separate approval.
6. **Check it:**
   - Read the ruleset back and compare each field with the file.
   - Confirm it reaches every production repo, and list any it misses by name.
   - Confirm the change shows up in the audit log.
   - Confirm a newly tagged repo picks it up without anyone configuring it.

If you'd rather run the commands yourself, tell me the org, the property or topic name, and the rules you want. I'll write the exact `gh api` commands, the ruleset JSON and the coverage check for you to paste.
