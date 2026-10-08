I couldn't edit `.gitlab-ci.yml` because the Write tool is disabled in this session, so nothing has changed. Here is the config I would have written:

```yaml
stages:
  - build
  - test

variables:
  npm_config_cache: "$CI_PROJECT_DIR/.npm"

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
    - npm ci --prefer-offline
    - npm run build
```

- **Not a new stage:** GitLab caching is a `cache:` setting, not a pipeline stage, so the stage list stays the same.
- **What gets cached:** `npm ci` deletes `node_modules` on every run, so caching that folder wouldn't help. The config caches npm's download cache (`.npm/`) instead. GitLab can only cache paths inside the project directory, which is why `npm_config_cache` points there.
- **Cache key:** The key is derived from `package-lock.json`. The cache is reused until the lockfile changes, then rebuilt.
- **Missing lockfile:** I found no `package-lock.json` in this workspace. `npm ci` fails without one, and the cache key needs it. If the lockfile lives elsewhere or has a different name (for example `yarn.lock` or `pnpm-lock.yaml`), the key and install command need adjusting.
- **`test` stage:** It has no jobs yet. When you add some, they inherit this cache through `default:`. Give them `policy: pull` so they only read it.
- **Runners:** If your runners are ephemeral and don't share storage, you'll also need a distributed cache (S3 or GCS) configured on the runner for the cache to persist between jobs.

If you enable Write or tell me to apply it another way, I'll make the change. I can also adapt it if you use a different package manager.
