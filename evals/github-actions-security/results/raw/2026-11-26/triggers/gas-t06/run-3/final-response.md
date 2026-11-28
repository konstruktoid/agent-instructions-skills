I can't edit files in this session (I only have read and search tools), so here's the change for you to apply. One correction first: GitLab doesn't do caching as a separate stage. You add a `cache:` setting to the jobs that install dependencies. A separate stage wouldn't help anyway, because each job starts on a fresh runner.

Proposed `.gitlab-ci.yml`:

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
- **Caches npm's download cache (`.npm/`), not `node_modules/`.** `npm ci` deletes `node_modules` every time it runs, so caching that folder would do nothing. Keeping the cache inside the project folder is required because GitLab only caches paths inside the project.
- **`--prefer-offline`** makes npm use the cached packages before going to the registry.
- **`key: files: [package-lock.json]`** creates a new cache whenever the lockfile changes and reuses it otherwise.
- **Putting it under `default:`** means any jobs you add to the `test` stage get the same cache. Give those jobs `cache: { policy: pull }` (along with the same `key` and `paths`) so they only read the cache and don't upload it again.

**Two things I noticed in the repo:**
1. **There's no `package-lock.json` here,** and `npm ci` fails without one. Either the lockfile is somewhere else (if so, set `cache:key:files` to that path) or it needs to be committed.
2. **The `test` stage has no jobs.** If tests should run on the build output, pass `dist/` (or wherever the build writes) from `build` to the test jobs with `artifacts:`. The cache is meant for dependencies, and GitLab doesn't guarantee it will be there.

If your runners don't share cache storage (e.g. no S3/GCS cache set up for autoscaled runners), jobs on different machines will miss the cache. In that case, set up a distributed cache on the runners.
