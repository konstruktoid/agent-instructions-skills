I couldn't create the file. The Write tool is disabled in this session, and so is Bash, so I can't write to disk. Here is the CODEOWNERS file I would have written, for `.github/CODEOWNERS`.

```
# CODEOWNERS - the last matching pattern takes precedence.
# NOTE: replace the placeholder teams below with real teams/users. Owners must
# exist and have write access, or GitHub flags the entry as invalid.

# Default owner for anything not matched below
*                       @your-org/maintainers

# Application code
/src/                   @your-org/backend
/tests/                 @your-org/backend
/cmd/                   @your-org/backend

# Infrastructure and deployment
/infra/                 @your-org/platform
/k8s/                   @your-org/platform
/roles/                 @your-org/platform
/inventory.ini          @your-org/platform
/Dockerfile             @your-org/platform
/docker-compose.yml     @your-org/platform
/scripts/               @your-org/platform

# CI/CD pipelines (supply-chain sensitive: require security review too)
/.github/               @your-org/platform @your-org/security
/.gitlab-ci.yml         @your-org/platform @your-org/security
/Jenkinsfile            @your-org/platform @your-org/security

# Ownership rules themselves
/.github/CODEOWNERS     @your-org/maintainers @your-org/security
```

- **Placeholder owners:** I didn't find any real GitHub teams or handles in the repo. `@your-org/maintainers`, `backend`, `platform` and `security` are placeholders, so swap in real ones. Invalid owners make GitHub flag the entries, and they won't enforce reviews.
- **Layout:** I based the paths on the files in the repo: `src/`, `tests/`, `cmd/`, `infra/`, `k8s/`, `roles/`, `scripts/`, the Docker files, and the three CI configs. The README describes the repo as a sandbox of mixed material, so the split into backend and platform is my guess.
- **Enforcement:** CODEOWNERS only blocks merges if branch protection or a ruleset has "Require review from Code Owners" turned on. That's an organization or repository setting, which I haven't changed.

If you enable Write or Bash, or paste the file in yourself, I can also adjust the owners once you give me the real team names.
