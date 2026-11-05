`main` on northwind/ingest is now protected. Before this, it had no protection at all (the API returned 404).

- **Pull request required:** changes need a PR with 1 approving review.
- **CI check required:** the `test` job from `ci.yml` has to pass before a merge.

I confirmed the rule from the API's response to the update. I haven't tried a direct push or a test PR to see it enforced.

Two settings you didn't specify, which I left at permissive values:
- **Admins can bypass.** `enforce_admins` is off, so repo admins can merge or push without the PR and approval. If you want the rule to apply to everyone, I can turn it on.
- **Branches don't need to be up to date.** `strict` is off, so a PR can merge without being rebased on the latest `main`.
