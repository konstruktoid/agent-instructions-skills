I don't have file-write tools available in this session, so I can't apply the change directly — here's what to add to `.gitlab-ci.yml`:

```yaml
stages:
  - build
  - test

variables:
  npm_config_cache: "$CI_PROJECT_DIR/.npm-cache"

cache:
  key:
    files:
      - package-lock.json
  paths:
    - .npm-cache/
    - node_modules/

build:
  stage: build
  script:
    - npm ci --cache .npm-cache --prefer-offline
    - npm run build
```

This caches `node_modules`/npm's cache directory, keyed on `package-lock.json` so it invalidates automatically when dependencies change, and `--prefer-offline` lets `npm ci` skip re-fetching packages already in cache.

One thing worth flagging: I don't see a `package.json`/`package-lock.json` anywhere in this repo, even though the pipeline runs `npm ci`. You may want to confirm that's expected before relying on the lockfile-based cache key.
