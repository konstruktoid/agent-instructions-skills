I can't edit files in this session (I only have read and search tools), so here's the change for you to apply.

In GitLab you don't need a separate stage for caching. You add the `cache:` keyword to the job that does the install, and GitLab restores the cache before the script runs and saves it after. Replace `.gitlab-ci.yml` with:

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

build:
  stage: build
  script:
    - npm ci --cache .npm --prefer-offline
    - npm run build
```

**What this does:**
- **It caches npm's download cache (`.npm/`), not `node_modules/`.** `npm ci` deletes `node_modules` on every run anyway, so caching it would be wasted work. With `--cache .npm --prefer-offline`, npm installs from the local tarballs and skips the network.
- **The cache key is a hash of `package-lock.json`.** The cache stays valid until your dependencies change, then GitLab builds a new one automatically.
- **The cache is under `default:`.** Any jobs you add later (for example in the empty `test` stage) get the same cache. Give those jobs `cache: { key: { files: [package-lock.json] }, paths: [.npm/], policy: pull }` so they only read it and don't upload it again.

**Things to check:**
- **There's no `package-lock.json` in the repo right now.** `npm ci` will fail without one, and the cache key falls back to `default`. Commit a lockfile first.
- **Caches are per-runner unless shared storage is set up.** On shared or autoscaled runners, the cache only carries between jobs if distributed caching (S3/GCS) is configured. Otherwise the first job on each runner still downloads everything.
- **Your `test` stage has no jobs yet.** If you want tests to reuse the build output rather than the dependency cache, pass it with `artifacts:`. Caches are a best-effort speed-up and aren't guaranteed to be there.
