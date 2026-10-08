I couldn't edit `.gitlab-ci.yml` because the Write tool is disabled in this session. Here is the change to apply by hand.

GitLab doesn't use a separate caching stage. Caching is a `cache:` setting on jobs, so the fix is to cache npm's download cache between pipelines and key it on the lockfile:

```yaml
stages:
  - build
  - test

variables:
  npm_config_cache: "$CI_PROJECT_DIR/.npm"   # GitLab can only cache paths inside the project dir

default:
  cache:
    key:
      files:
        - package-lock.json                  # new cache only when dependencies change
    paths:
      - .npm/
    policy: pull-push

build:
  stage: build
  script:
    - npm ci --prefer-offline
    - npm run build
```

- **What's cached:** I cache `.npm/`, not `node_modules`. `npm ci` deletes `node_modules` every run, so caching it wouldn't help. With a warm cache, `npm ci` still runs but reinstalls from local files instead of downloading.
- **Cache key:** The key comes from `package-lock.json`, so it changes only when dependencies change.
- **Test jobs:** Because the cache is under `default:`, future `test` jobs get it too. Once they exist, set `policy: pull` on them so only `build` writes the cache.
- **Missing files:** I found no `package.json` or lockfile in this workspace. `npm ci` needs a committed `package-lock.json`, and the cache key points at that file. If your lockfile lives in a subdirectory, change the `files:` path to match.
- **Untested:** I haven't run this in a pipeline. You can check the first run for "Creating cache" and the second for "Successfully extracted cache".

This is a GitLab pipeline, so I didn't use the GitHub Actions security skill.
