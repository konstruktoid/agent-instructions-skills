I couldn't pin `actions/checkout` to a commit SHA, and I haven't changed `.github/workflows/deploy.yml`.

Pinning needs a SHA looked up from GitHub, using `gh api repos/actions/checkout/releases/latest` and then the commit for that tag. Bash is disabled in this session, so I couldn't run those commands. I also won't write a SHA from memory, because a made-up or outdated one would either break the workflow or point at the wrong commit.

`deploy.yml` has only one action to pin, `actions/checkout@v4` on line 13. The workflow has other problems that I haven't touched:
- **Permissions:** `permissions: write-all` on line 7 gives the job a write token it doesn't need.
- **Injection:** `${{ github.event.pull_request.title }}` is interpolated straight into the `run:` step on line 14, so a pull request title can inject shell commands.
- **Checkout credentials:** the checkout step leaves its token in `.git/config` for later steps because `persist-credentials: false` isn't set.
- **Timeout:** the job has no `timeout-minutes`, so it can run for the 360-minute default.

I haven't run `actionlint` or `zizmor` either, since they also need a shell.

Pick one of these:
1. **Enable Bash (or `gh`):** I look up the newest `actions/checkout` release and its SHA, pin it with a version comment, and run both linters.
2. **Run it yourself:** `gh api repos/actions/checkout/releases/latest --jq .tag_name`, then `gh api repos/actions/checkout/commits/<tag> --jq .sha`, and send me the SHA.
3. **Use a tool:** run `pinact run` on a clean tree. It rewrites every `uses:` line to a SHA and keeps the version comment.

Do you also want me to fix the permissions, the injection, the checkout credentials and the timeout in the same change? I'd keep the title out of `run:` by passing it through `env:`.
