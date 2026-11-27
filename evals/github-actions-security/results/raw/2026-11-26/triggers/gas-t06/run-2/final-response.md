I couldn't change your pipeline. There's a `.gitlab-ci.yml` in the workspace, but you declined the request to read it, and I don't have a tool here that can edit files. So below is a caching setup you can adapt. If you paste the file or allow the read, I'll fit it to your actual stack.

The usual approach in GitLab CI isn't a separate stage. You add a `cache:` block keyed on your lockfile, so the cache stays valid until your dependencies change:

```yaml
default:
  cache: &deps_cache
    key:
      files:
        - package-lock.json        # or poetry.lock / requirements.txt / go.sum / Gemfile.lock
    paths:
      - .npm/                      # the package manager's download cache
    policy: pull                   # most jobs only read the cache

variables:
  npm_config_cache: "$CI_PROJECT_DIR/.npm"   # GitLab can only cache paths inside the project dir

stages: [install, test, build]

install_deps:
  stage: install
  cache:
    <<: *deps_cache
    policy: pull-push              # only this job uploads the cache
  script:
    - npm ci --prefer-offline

test:
  stage: test
  script:
    - npm ci --prefer-offline      # fast because the downloads come from the cache
    - npm test
```

The equivalent settings for other stacks:

| Stack | Cache path | Variable to set | Key file |
|---|---|---|---|
| pip | `.cache/pip` | `PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"` | `requirements.txt` |
| Poetry | `.cache/pypoetry` | `POETRY_CACHE_DIR: ...` | `poetry.lock` |
| Go | `.go/pkg/mod` | `GOPATH: "$CI_PROJECT_DIR/.go"` | `go.sum` |
| Bundler | `vendor/ruby` | `BUNDLE_PATH: vendor/ruby` | `Gemfile.lock` |
| Maven | `.m2/repository` | `MAVEN_OPTS: "-Dmaven.repo.local=$CI_PROJECT_DIR/.m2/repository"` | `pom.xml` |

Things to keep in mind:
- **Cache vs. artifacts:** GitLab treats the cache as best-effort, so it can be missing. Every job still needs to run the install command; with a warm cache it just finishes quickly. If later jobs must get exactly what was installed, pass the installed directory (for example `node_modules/`) between jobs as an artifact instead.
- **Runners:** if your runners don't share a cache store such as S3 or GCS, each runner keeps its own cache. That will look like the cache sometimes being missed.
- **Protected branches:** GitLab keeps caches for protected and unprotected branches separate by default. Leave that on so that merge request pipelines can't poison the cache that main uses.

Tell me your package manager, or let me read the file, and I'll write the exact change.
