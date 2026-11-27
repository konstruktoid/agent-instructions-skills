I couldn't write the file because this session has no file-writing tool, only read and search. The README also doesn't name any owners or teams, so the handles below are placeholders based on the repo layout. Replace them with real GitHub users or teams, then save the file as `.github/CODEOWNERS`:

```gitignore
# CODEOWNERS — for each changed file, the last matching pattern wins.
# Owners must have write access to the repository, or GitHub ignores them.

# Default owner for anything not matched below
*                           @ORG/maintainers

# Application code
/src/                       @ORG/python-devs
/tests/                     @ORG/python-devs
/cmd/                       @ORG/go-devs

# Infrastructure and deployment
/infra/                     @ORG/platform
/k8s/                       @ORG/platform
/roles/                     @ORG/platform
/inventory.ini              @ORG/platform
/Dockerfile                 @ORG/platform
/docker-compose.yml         @ORG/platform
/scripts/                   @ORG/platform

# CI/CD pipelines: changes here can expose secrets and the release path
/.github/workflows/         @ORG/security @ORG/platform
/.gitlab-ci.yml             @ORG/security @ORG/platform
/Jenkinsfile                @ORG/security @ORG/platform

# Protect this file itself
/.github/CODEOWNERS         @ORG/maintainers
```

A few things to know:
- **It's last so it wins:** for each file, the last pattern that matches decides the owner. That's why the catch-all `*` is at the top and the CODEOWNERS line is at the bottom.
- **Owners must have write access:** a team or user without write access to the repo is silently ignored. Run the file check under the repo's **Settings → Code owners** view, or look for the errors banner on the file's page on GitHub, to find these.
- **It only enforces anything with branch protection:** the file just assigns reviewers until you turn on **"Require review from Code Owners"** in a branch protection rule or ruleset on the default branch.
- **CI files have two owners:** I gave the pipeline files to both a security team and the platform team because those files touch secrets. Either team's approval is enough. If you want one review to cover everything, drop the extra team.

Send me the real team names and I'll fill them in.
