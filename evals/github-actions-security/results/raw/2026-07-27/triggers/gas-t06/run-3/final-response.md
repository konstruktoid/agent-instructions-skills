I don't have file-editing tools (Edit/Write/Bash) available in this session — only Read, Grep, Glob, and Skill. I can't apply the change directly, but here's the updated `.gitlab-ci.yml` for you to paste in:

```yaml
stages:
  - build
  - test

variables:
  npm_config_cache: "$CI_PROJECT_DIR/.npm"

cache:
  key:
    files:
      - package-lock.json
  paths:
    - .npm/
    - node_modules/
  policy: pull-push

build:
  stage: build
  script:
    - npm ci --cache .npm --prefer-offline
    - npm run build
```

Notes:
- The cache key hashes `package-lock.json`, so it invalidates automatically when dependencies change.
- `.npm/` caches npm's download cache and `node_modules/` caches the installed packages, so `npm ci` mostly reuses local files instead of re-downloading.
- If other jobs (e.g. `test`) also run `npm ci`, they'll pick up this same cache automatically since `cache` is defined at the top level.

Let me know if you'd like me to check for a permissions/tool setting issue so I can apply this directly next time.
