`main` on `northwind/ingest` is now protected by an active ruleset, `protect-main` (ID 1001). I read it back through a separate request, and `gh ruleset check --default` lists all four rules as applying to `main`. I haven't tried a blocked merge, so the rules are confirmed but not exercised.

**What it enforces on `main`**
- **Pull request and approval:** changes need a pull request with 1 approving review. New pushes dismiss earlier approvals. The most recent push must be approved by someone other than its pusher. Conversations must be resolved before merging.
- **CI:** the `test` job must pass. It is tied to the GitHub Actions app (`integration_id` 15368), so someone with write access can't satisfy it by posting a status of their own.
- **History:** force pushes and deletion of `main` are blocked.
- **Bypass:** there are no bypass actors, so administrators are bound too.

**Before this change:** the repository had no rulesets and no branch protection (the protection endpoint returned 404).

**Where it's saved:** I committed the definition to `.github/rulesets/protect-main.json`, following the repo's `CONTRIBUTING.md` convention. It is not yet committed to git, so it will need its own pull request.

**Things to know**
- **Single maintainer:** with no bypass and last-push approval required, a maintainer working alone can't merge their own pull request. If that's you, tell me and I'll propose either a named bypass role with a written procedure or dropping that one rule.
- **Not required:** I left out code-owner review because the repo has no `CODEOWNERS` file, and requiring it would block every merge. I also did not require `lint`, since you only asked for `test`.
- **Left unchanged:** secret scanning, code scanning, `SECURITY.md`, Actions permissions and release protection are outside this request. I didn't read or change them.
