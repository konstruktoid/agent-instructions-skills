I can't apply this myself because I don't have a file-editing tool in this session, so here's the change to paste into `.gitlab-ci.yml`.

In GitLab you don't add a separate stage for caching. You add a `cache:` setting to the jobs that install dependencies, and GitLab restores the cache before the job runs and saves it afterwards. A separate stage wouldn't speed up `npm ci` in other jobs.

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

**Notes**

- **Why it caches `.npm/` and not `node_modules/`:** `npm ci` deletes `node_modules` every time it runs, so caching that folder would do nothing. This caches npm's download store instead, and `--prefer-offline` installs from it without going to the registry.
- **Why `.npm` is inside the project folder:** GitLab can only cache paths inside the project directory, which is why `--cache .npm` points there and not at the default `~/.npm`.
- **When the cache resets:** it's keyed on `package-lock.json`, so it starts fresh whenever dependencies change. Old caches won't get reused after an upgrade.
- **Jobs that only read the cache:** your `test` stage has no jobs yet. When you add one, give it `cache: { key: { files: [package-lock.json] }, paths: [.npm/], policy: pull }`. That way it reads the cache but doesn't spend time uploading it again.
- **If `build` output is needed later:** to pass build output on to `test`, use `artifacts:` for that, not the cache. GitLab doesn't guarantee the cache will be there, but artifacts are always passed on.
- **Lockfile check:** there's no `package-lock.json` (or `package.json`) in this workspace. Make sure the lockfile is committed in the real repo. The cache key depends on it, and `npm ci` won't run without it.
