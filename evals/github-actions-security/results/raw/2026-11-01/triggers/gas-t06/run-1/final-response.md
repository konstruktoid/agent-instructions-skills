I can't edit files in this session (I only have read and search tools), so here's the change to apply to `.gitlab-ci.yml` yourself.

One thing to know first: GitLab doesn't use a separate stage for caching. You add a `cache:` setting to the jobs, and GitLab restores the cache before the job runs and saves it afterwards. A new stage would just add a job that does nothing.

```yaml
stages:
  - build
  - test

default:
  cache:
    key:
      files:
        - package-lock.json
    paths:
      - .npm/
    policy: pull-push

variables:
  npm_config_cache: "$CI_PROJECT_DIR/.npm"

build:
  stage: build
  script:
    - npm ci --prefer-offline --no-audit
    - npm run build
```

**Why it's set up this way:**
- **It caches `.npm/`, not `node_modules/`.** `npm ci` deletes `node_modules` every time it runs, so caching that folder wouldn't help. Caching npm's download store means packages come from the cache instead of the registry.
- **`npm_config_cache` moves npm's cache into the project folder.** GitLab can only cache files inside the project directory.
- **The cache key comes from `package-lock.json`.** The cache stays valid until your dependencies change, then a new one is built automatically.
- **`--prefer-offline`** makes npm use cached packages instead of checking the registry for each one.

**Worth checking:**
1. **No `package-lock.json` is committed.** `npm ci` fails without one, so the current job probably can't work as it is. If no lock file exists, GitLab also falls back to a single key called `default` and the cache never refreshes. Commit a lock file first.
2. **Your `test` stage has no jobs yet.** When you add them, they get this cache through `default:`. If a job only installs and never adds packages, set `cache: { key: { files: [package-lock.json] }, paths: [.npm/], policy: pull }` on it so it doesn't upload the cache again.
3. **To skip the install entirely in test jobs,** pass the built output from `build` as `artifacts:` rather than reinstalling.
4. **On autoscaled or shared runners,** the cache only carries between jobs if a shared cache (such as S3 or GCS) is configured for the runner. Otherwise each job may land on a machine that doesn't have it.
