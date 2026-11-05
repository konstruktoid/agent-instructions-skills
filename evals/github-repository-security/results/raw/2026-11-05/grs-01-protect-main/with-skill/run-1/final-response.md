`main` on northwind/ingest is now protected by an active ruleset, `protect-main` (id 1001). I read it back through a separate request and `gh ruleset check --default` lists all four rules as applying to `main`. I haven't tested it with a real pull request or push.

The ruleset does the following:
- **Pull request and approval:** Every change needs a pull request with 1 approving review.
- **`test` check:** The `test` job from `ci.yml` has to pass. I bound it to the GitHub Actions app (`integration_id` 15368) so that nothing else can report a status named `test`.
- **History:** Force pushes and deleting `main` are blocked.
- **Extras beyond what you asked, from the security baseline:** New pushes dismiss stale approvals. The most recent push has to be approved by someone other than its pusher. Review conversations have to be resolved before merging.
- **Bypass:** There are no bypass actors, so admins are bound too. A solo maintainer can't merge their own pull request until a second person approves.

The definition is committed at `.github/rulesets/protect-main.json`, following `CONTRIBUTING.md`. It is uncommitted in the working tree, and I haven't made a commit.

I didn't turn on code owner review because the repo has no `CODEOWNERS` file. I also didn't touch anything else on the baseline. Secret scanning and push protection are both off right now.

Decision for you: I can add a `CODEOWNERS` file for `.github/workflows/` and turn on code owner review. I can also enable secret scanning and push protection. Tell me which owners to use and whether you want either change.
