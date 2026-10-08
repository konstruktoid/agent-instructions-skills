I couldn't edit `.gitlab-ci.yml`. The Write tool is disabled in this session, and I have no other way to modify files. Here is the change to apply by hand.

You don't need a separate caching stage. GitLab restores and saves the cache around each job, so a stage would only add a job that does nothing useful. The fix is a `cache` block that keeps npm's download cache between pipelines:

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

- **Cache location:** `npm ci` deletes `node_modules` every run, so caching `node_modules` gains nothing. Caching the download cache in `.npm/` avoids re-fetching packages. GitLab can only cache paths inside the project directory, which is why `npm_config_cache` points there.
- **Cache key:** the key is tied to `package-lock.json`. The cache is rebuilt only when the dependencies change.
- **Offline installs:** `--prefer-offline` makes npm use the cache before going to the network.
- **Test jobs:** if your `test` jobs also run `npm ci`, they pick up the same cache through `default`. Set `policy: pull` on them so they only read it.

I found no `package-lock.json` in the workspace. `npm ci` requires one, and the cache key depends on it. If the file lives in a subdirectory or isn't committed, tell me and I'll adjust the key and path.

If you can re-enable file writes, I'll apply the change directly.
