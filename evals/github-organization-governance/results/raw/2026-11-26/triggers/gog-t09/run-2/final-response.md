I couldn't create the file because I have no file-writing tool in this session. Below is a ready-to-use `.github/CODEOWNERS` based on the repository's layout. Save it at that path.

The team handles (`@your-org/...`) are placeholders. Nothing in the repo names an organization or any teams, so swap in your real ones:

```gitignore
# CODEOWNERS — the last matching pattern wins, so put broad rules first.
# Every handle must be a user or team with write access, or GitHub ignores the line.

# Default owner for anything not matched below
*                           @your-org/maintainers

# CI/CD pipelines: changes here can run code with repository secrets
/.github/                   @your-org/platform @your-org/security
/.gitlab-ci.yml             @your-org/platform @your-org/security
/Jenkinsfile                @your-org/platform @your-org/security

# Containers and orchestration
/Dockerfile                 @your-org/platform
/docker-compose.yml         @your-org/platform
/k8s/                       @your-org/platform

# Infrastructure as code and configuration management
/infra/                     @your-org/infrastructure
/roles/                     @your-org/infrastructure
/inventory.ini              @your-org/infrastructure
/scripts/                   @your-org/infrastructure

# Application code
/src/ledger/                @your-org/ledger
/tests/                     @your-org/ledger
/cmd/                       @your-org/backend

# Protect this file itself
/.github/CODEOWNERS         @your-org/maintainers @your-org/security
```

**Design choices:**
- **CI files are co-owned by security.** `deploy.yml`, `.gitlab-ci.yml` and `Jenkinsfile` all run with pipeline credentials, so a security reviewer should see changes to them.
- **The ownership rules are protected too.** The final line stops someone from quietly changing who owns what. Because it comes after `/.github/`, it overrides that rule for this one file.
- **Tests belong to the ledger team.** The only test file is `tests/test_balance.py`. If you add tests for `cmd/`, use more specific patterns.

**Making it enforceable:** owners only become required reviewers once you turn on **"Require review from Code Owners"** in a branch protection rule or ruleset for the default branch. Without that setting, owners are just requested as reviewers.

**Checking it:** after you push, open the file on GitHub. It flags any line with an unknown owner or a team that lacks write access.
