I don't have a file-editing tool available in this session (only Glob/Grep/Read/Skill), so I can't apply the change directly. Here's the updated `.gitlab-ci.yml` for you to add — cache keyed on `package-lock.json` so `npm ci` reuses `node_modules` and the npm cache across runs, instead of installing on every pipeline:

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
      - node_modules/
      - .npm/

build:
  stage: build
  script:
    - npm ci --cache .npm --prefer-offline
    - npm run build
```

Notes:
- The cache key is derived from `package-lock.json`'s content, so it invalidates automatically when dependencies change.
- `npm ci --cache .npm --prefer-offline` points npm's cache at the cached `.npm/` directory and avoids re-fetching from the registry when it's already warm.
- There's no `package-lock.json` in this repo currently, so `npm ci` will fail regardless of caching — you'll want one committed for this to work at all.

If you'd like, I can try again once file-editing tools are enabled for this session.
