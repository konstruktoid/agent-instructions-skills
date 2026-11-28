I couldn't create the file because I only have read and search tools in this session. Below is the full content. Save it as `.github/CODEOWNERS`.

```gitignore
# CODEOWNERS — https://docs.github.com/articles/about-code-owners
# When several patterns match a file, the last one wins, so the most specific rules are at the bottom.
# Replace the @your-org/* teams with real teams. Each team needs write access to the repo.

# Default owner for anything not matched below
*                           @your-org/maintainers

# Application code
/src/                       @your-org/python
/tests/                     @your-org/python
/cmd/                       @your-org/go

# Scripts
/scripts/                   @your-org/platform

# Infrastructure and configuration management
/infra/                     @your-org/platform
/k8s/                       @your-org/platform
/roles/                     @your-org/platform
/inventory.ini              @your-org/platform

# Containers
/Dockerfile                 @your-org/platform
/docker-compose.yml         @your-org/platform

# CI/CD: a change here can change how code gets built, deployed or approved
/.github/workflows/         @your-org/platform @your-org/security
/.gitlab-ci.yml             @your-org/platform @your-org/security
/Jenkinsfile                @your-org/platform @your-org/security

# Protect this file so nobody can quietly reassign ownership
/.github/CODEOWNERS         @your-org/security
```

**What I assumed:**
- **Team names are placeholders.** Nothing in the repo shows the GitHub org or any teams. Swap in real `@org/team` handles or usernames. GitHub ignores entries it can't resolve, and when that happens the path has no owner at all.
- **The ownership split** follows the repo layout: Python for `src/` and `tests/`, Go for `cmd/`, and platform for infrastructure, Ansible and containers. CI/CD files and CODEOWNERS itself also need a security reviewer.

**This file doesn't enforce anything by itself.** It only requests reviews. To actually require owner approval, turn on "Require review from Code Owners" in a branch protection rule or ruleset on the default branch.

Tell me the real team names and I can fill them in. If you give me write access, I'll create the file directly.
