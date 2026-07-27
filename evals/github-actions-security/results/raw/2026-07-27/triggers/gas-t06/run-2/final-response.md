I don't have file-editing tools available in this session, so I can't apply this directly — here's the change to add caching, keyed on `package-lock.json` so it only invalidates when dependencies change:

```yaml
stages:
  - build
  - test

cache:
  key:
    files:
      - package-lock.json
  paths:
    - node_modules/
    - .npm/

build:
  stage: build
  script:
    - npm ci --cache .npm --prefer-offline
    - npm run build
```

Notes:
- The `cache` block is top-level so it applies to every job (add a `test` job under the same key later and it'll reuse the cache too).
- `npm ci` deletes `node_modules` before installing, so caching it doesn't skip much — the real win is caching `.npm/` (npm's download cache) via `--cache .npm --prefer-offline`, which avoids re-downloading packages while still keeping `npm ci`'s lockfile-integrity guarantees.
- Cache key is `package-lock.json`'s hash, so it invalidates automatically when dependencies change and reuses across pipelines otherwise (default `cache.policy` is pull-push).

There's no `package-lock.json` in this repo currently — confirm the actual lockfile path before applying, or add `policy: pull` to jobs that only consume the cache if you split build/test later.
