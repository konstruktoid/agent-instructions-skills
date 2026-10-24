I couldn't edit the file because I don't have a write tool in this session. Here is the change to paste into `.gitlab-ci.yml`.

GitLab doesn't need a separate stage for caching. You add a `cache:` block to the job (or to `default:` so every job uses it):

```yaml
stages:
  - build
  - test

default:
  image: node:22
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

**What this does:**
- **It caches `.npm/`, not `node_modules/`.** `npm ci` deletes `node_modules` on every run, so caching that folder wouldn't help. Caching npm's download cache means `npm ci` still installs, but from local files instead of the network.
- **The cache key comes from `package-lock.json`.** The cache is reused until your dependencies change, then it's rebuilt automatically.
- **`npm_config_cache` points npm at a folder inside the project.** GitLab can only cache paths under `$CI_PROJECT_DIR`.
- **`--prefer-offline`** tells npm to use the cached copy before checking the registry.

**Things to check:**
1. **Image:** I added `image: node:22` as a guess. Change it or remove it to match your runner setup.
2. **Test jobs:** the `test` stage has no jobs yet. When you add them, they'll use the same cache. If they only read it, set `cache: { policy: pull }` on them so they don't upload it again.
3. **Runner setup:** if your runners don't share a cache (several runners without S3 or GCS cache configured), a job won't find the cache when it lands on a different machine. In that case you'd need to set up distributed caching on the runners.
4. **Skipping the install entirely:** if you want later jobs to skip `npm ci`, pass `node_modules/` from `build` to them as an `artifact` rather than a cache.
