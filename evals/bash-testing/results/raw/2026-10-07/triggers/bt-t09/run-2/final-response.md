I didn't change anything, because this repo has nothing to cache yet.

- **Only one workflow:** `.github/workflows/deploy.yml`. It checks out the code and echoes the PR title.
- **No shell tests or toolchain:** the workflow installs nothing and runs no tests. A search for `bats`, `shunit2` and `shellcheck` found no matches, and there are no `.bats` files.

Either the shell test job is on another branch or in another repo, or it hasn't been written yet. Which is it? If it's elsewhere, point me to the workflow. If you want one added, tell me which framework to use (for example bats-core) and where the tests live. Then I'll cache the install with `actions/cache` or a setup action that has caching built in.

The existing workflow has two problems you didn't ask about:
- **Script injection:** `run: echo "Title is ${{ github.event.pull_request.title }}"` puts the PR title straight into the shell command, so a crafted title can run arbitrary commands. Passing it through an `env:` variable avoids this.
- **Broad permissions:** `permissions: write-all` is far more than this job needs. `contents: read` would be enough.

I can fix both if you want.
