I couldn't create the file. This session has no file-writing tool and Bash is disabled. Below is the content to save as `.github/CODEOWNERS`.

The repo has no existing CODEOWNERS file, team names, or maintainer info, and I couldn't read git history. So the team handles are placeholders. Replace them with real teams from your org.

```
# CODEOWNERS
# The last matching pattern wins, so keep the broad rule first and the specific ones after it.

# Default owner for anything not matched below
*                           @your-org/maintainers

# Application code (Python ledger service and Go parser)
/src/                       @your-org/backend
/cmd/                       @your-org/backend
/tests/                     @your-org/backend

# Infrastructure as code and configuration management
/infra/                     @your-org/platform
/roles/                     @your-org/platform
/inventory.ini              @your-org/platform
/k8s/                       @your-org/platform

# Container builds and local environment
/Dockerfile                 @your-org/platform
/docker-compose.yml         @your-org/platform

# CI/CD pipelines. These run with deploy credentials, so require security review too.
/.github/                   @your-org/platform @your-org/security
/.gitlab-ci.yml             @your-org/platform @your-org/security
/Jenkinsfile                @your-org/platform @your-org/security

# Operational scripts (backup.sh copies data off-host)
/scripts/                   @your-org/platform @your-org/security

# Ownership rules themselves
/.github/CODEOWNERS         @your-org/maintainers
```

- **Location:** `.github/CODEOWNERS` is a valid location. The `/.github/` rule gives CI workflows to platform and security, and the last line then hands the CODEOWNERS file itself to maintainers.
- **Branch protection:** CODEOWNERS only blocks merges if the branch protection rule or ruleset has "Require review from Code Owners" turned on.
- **Write access:** Each team must have write access to the repo, or GitHub ignores its entries.
- **Validation:** After saving, open the file in the GitHub UI. It flags invalid owners and syntax errors.

If you give me the real team or user handles, or enable file writes, I'll create the file with those handles filled in.
