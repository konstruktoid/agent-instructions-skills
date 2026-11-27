I can't edit files in this session because I only have read and search tools. Here's the change to make in `.gitlab-ci.yml`.

GitLab doesn't need a separate caching stage. Caching is set with the `cache:` keyword on jobs, and a separate stage would only add another job without stopping the reinstall. The right fix is a cache that every job shares:

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
- **It caches `.npm/`, not `node_modules/`.** `npm ci` deletes `node_modules` every time it runs, so caching that folder would be wasted. Caching npm's download store instead means `npm ci` installs from local files rather than downloading packages again.
- **`npm_config_cache`** puts npm's store inside the project directory. GitLab can only cache paths under `$CI_PROJECT_DIR`, and npm's default (`~/.npm`) is outside it.
- **`key: files: [package-lock.json]`** keeps the cache until the lockfile changes, then starts a new one.
- **Putting it under `default:`** means any test job you add later gets the cache automatically. Jobs that only read the cache can set `cache: { policy: pull }` so they don't upload it again.

**Things I noticed in the repo:**
1. **There's no `package-lock.json` in the workspace.** `npm ci` fails without one, and the cache key needs it. Commit a lockfile, or tell me if it's somewhere else.
2. **The `test` stage has no jobs.** If you're planning one, I can add it with `policy: pull`.
3. **To also skip `npm ci` in test jobs,** pass the build output to them with `artifacts:` (for example `dist/`, or `node_modules/` if they need it) and `needs: [build]`. Artifacts are reliable within a single pipeline run. The cache is best-effort, especially when runners don't share cache storage.

If you turn on file editing, I can apply this directly.
