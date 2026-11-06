`main` on northwind/ingest is now protected. I didn't re-query the branch afterwards, but GitHub's response to the update showed these settings:

- **Pull request with one approval:** changes must go through a pull request, and it needs 1 approving review.
- **`test` must pass:** the `test` job from `.github/workflows/ci.yml` is a required status check.
- **Branch must be up to date:** I turned on strict mode, so a PR has to be current with `main` before it merges. You didn't ask for this. It can mean extra rebases or merges, and it's a single flag if you'd rather drop it.
- **Admins included:** I turned on `enforce_admins`, so admins can't bypass the rules either. You didn't ask for this one either.
- **No force pushes or deletion:** both are blocked on `main`.

Before this, `main` had no protection at all (the protection endpoint returned 404).
