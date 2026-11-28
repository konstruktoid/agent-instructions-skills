I couldn't edit the file because I only have read and search tools in this session. Here's the change to paste into `.gitlab-ci.yml`.

You don't need a separate caching stage. In GitLab, caching is set per job with the `cache:` keyword, and it's restored before `script` runs. Your file currently has one job (`build`), and it runs `npm ci`:

```yaml
stages:
  - build
  - test

.npm_cache: &npm_cache
  key:
    files:
      - package-lock.json   # new cache only when dependencies change
  paths:
    - .npm/

build:
  stage: build
  cache:
    <<: *npm_cache
    policy: pull-push        # restores the cache and saves it after the job
  script:
    - npm ci --cache .npm --prefer-offline
    - npm run build
```

**Why it's set up this way:**
- **It caches `.npm/`, not `node_modules/`.** `npm ci` deletes `node_modules` at the start of every run, so caching that folder wouldn't help. Caching npm's download cache means packages come from the runner's cache instead of the registry.
- **`--cache .npm`** moves npm's cache into the project folder. GitLab can only cache paths inside the project directory, and npm's default is `~/.npm`.
- **The cache key comes from `package-lock.json`.** The cache stays valid until your dependencies change, then a fresh one is built automatically.
- **`--prefer-offline`** tells npm to use cached packages without checking the registry first.

**When you add jobs to the `test` stage** (it has none yet), give them `cache: { <<: *npm_cache, policy: pull }`. They'll read the cache without uploading it again. If they need the built output, pass it from `build` with `artifacts:` (for example `artifacts: { paths: [dist/] }`) rather than the cache. GitLab doesn't guarantee a cache will be there, so it shouldn't carry anything a later job depends on.

**Things to check:**
- I didn't find a `package-lock.json` in this workspace. Both `npm ci` and the cache key need it, so make sure it's committed. If it's missing, the key falls back to `default` and the cache never updates when dependencies change.
- On runners with autoscaling or several machines, caches stay on each machine unless you set up a shared cache store (such as S3 or GCS) in the runner config. Without that, a job that lands on a different machine starts with an empty cache.

If you want me to write the file instead, give me write permission and I'll apply it.
