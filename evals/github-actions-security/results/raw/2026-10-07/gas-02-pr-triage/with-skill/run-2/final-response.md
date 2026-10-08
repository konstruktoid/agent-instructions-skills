I added a triage workflow that comments on and labels newly opened pull requests, including ones from forks. I haven't run it on GitHub. actionlint reports no findings. zizmor reports one low finding, a missing `concurrency` setting in the existing `ci.yml`, which I left alone.

- **Workflow:** `.github/workflows/triage.yml` runs when a pull request is opened. It posts "Welcome, @username…" and repeats the pull request title, shown in a code block. It then applies `needs-triage` and creates that label first if it doesn't exist.
- **Fork support:** It uses the `pull_request_target` trigger, because a fork's `pull_request` token is read-only and can't comment or label. The workflow never checks out or runs pull request code. It reads only event data, passed through environment variables, and its only permission is `pull-requests: write`.
- **Suppression:** zizmor flags `pull_request_target` as a dangerous trigger. I added `zizmor.yml` to suppress that finding for `triage.yml` only, with the reason in a comment. You didn't ask for that file, so check you're happy with it.
- **Title display:** The title goes in a code block so an `@mention` in it can't notify anyone.
- **README:** I added a "Triage workflow" section describing the above.

I didn't commit anything. A real pull request from a fork would confirm the comment and label work. I'd need your go-ahead before pushing a branch to test that.
