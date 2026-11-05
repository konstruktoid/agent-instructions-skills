I couldn't create the file. The Write tool is disabled in this session, and I have no other way to write files here. Below is the CODEOWNERS I intended to save as `.github/CODEOWNERS`. You can paste it in, or re-enable Write and I'll create it.

```
# CODEOWNERS
# The last matching pattern wins, so keep the broad default first and the
# specific paths after it.
#
# TODO: replace @your-org/... with real teams. Owners must be users or teams
# with write access to this repository, or GitHub ignores the line.

# Default owner for anything not matched below
*                           @your-org/maintainers

# Application code
/src/                       @your-org/backend
/tests/                     @your-org/backend
/cmd/                       @your-org/backend

# Infrastructure, deployment and configuration management
/infra/                     @your-org/platform
/k8s/                       @your-org/platform
/roles/                     @your-org/platform
/inventory.ini              @your-org/platform
/Dockerfile                 @your-org/platform
/docker-compose.yml         @your-org/platform
/scripts/                   @your-org/platform

# CI/CD pipelines: changes here can alter what runs with repository secrets
/.github/                   @your-org/security @your-org/platform
/.gitlab-ci.yml             @your-org/platform
/Jenkinsfile                @your-org/platform

# Ownership rules themselves
/.github/CODEOWNERS         @your-org/security
```

- **Placeholder owners:** The repo and its README don't name an organization or any teams, so `@your-org/maintainers`, `backend`, `platform` and `security` are placeholders I made up. Replace them with real teams or users. GitHub ignores owners that don't exist or lack write access, and it shows those lines as errors in the file view.
- **Grouping by path:** I grouped paths from the repo layout. `src/`, `tests/` and `cmd/` (Python and Go) go to a backend team. Terraform, Kubernetes, Ansible, Docker and the scripts go to a platform team. Pipeline files go to security plus platform.
- **Pipeline ownership:** Pipeline files can change what runs with repository secrets, so I gave them stricter ownership. The `/.github/CODEOWNERS` line is last so it overrides the broader `/.github/` rule and only security owns the file.
- **Review enforcement:** CODEOWNERS only requests reviews. To make them mandatory, turn on "Require review from Code Owners" in a branch protection rule or ruleset for `main`.
