I couldn't edit the file because this session can't write files. Here's the change to make to `.gitlab-ci.yml` yourself.

In GitLab, caching is set with the `cache:` keyword on each job, not as its own stage. A separate "cache" stage wouldn't stop the reinstall: the later jobs would still have to run `npm ci`. Here is the setup I'd use:

```yaml
stages:
  - build
  - test

.npm-cache: &npm-cache
  key:
    files:
      - package-lock.json
  paths:
    - .npm/

build:
  stage: build
  cache:
    <<: *npm-cache
    policy: pull-push
  script:
    - npm ci --cache .npm --prefer-offline
    - npm run build
```

**Why it works this way:**
- **It caches npm's download cache (`.npm/`), not `node_modules/`.** `npm ci` deletes `node_modules` every time it runs, so caching that folder would do nothing. With the download cache in place, `npm ci` installs from local copies instead of downloading every package again.
- **The cache key comes from `package-lock.json`.** The cache is reused until your dependencies change, and then it's rebuilt automatically.
- **`--prefer-offline`** tells npm to use the cached copies and skip checking the registry for each package.
- **Test jobs:** your `test` stage has no jobs yet. When you add them, use `cache: { <<: *npm-cache, policy: pull }`. They'll read the cache without uploading it again, which saves time at the end of each job.

**Two things to check:**
1. This repo has no `package-lock.json` in it. `npm ci` fails without one, and the cache key depends on it, so commit the lockfile.
2. If test jobs need the build output (e.g. `dist/`), pass it from `build` with `artifacts:`, not the cache. GitLab doesn't guarantee a cache will be there, so jobs can't rely on it.
