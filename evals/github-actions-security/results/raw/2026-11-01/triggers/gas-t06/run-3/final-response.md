I couldn't make this change myself. I don't have a file-editing tool in this session, so here is the updated `.gitlab-ci.yml` for you to paste in.

GitLab doesn't need a separate stage for this. Its `cache:` keyword keeps files between pipeline runs, and any job can use it. A stage only sets the order jobs run in, so adding one wouldn't stop the install from repeating.

```yaml
stages:
  - build
  - test

default:
  cache: &npm_cache
    key:
      files:
        - package-lock.json
    paths:
      - .npm/
    policy: pull

build:
  stage: build
  cache:
    <<: *npm_cache
    policy: pull-push
  script:
    - npm ci --cache .npm --prefer-offline
    - npm run build
```

What this does:

- **Caches `.npm/`, not `node_modules/`.** `npm ci` deletes `node_modules` every time it runs, so caching that folder wouldn't help. Caching npm's download cache does help: with `--prefer-offline`, npm installs from the cached files instead of downloading them again. The cache has to be inside the project folder (`--cache .npm`) because GitLab can only cache paths there.
- **The cache key comes from `package-lock.json`.** When your dependencies change, the job starts with a fresh cache. Otherwise every pipeline reuses the same one.
- **Only `build` saves the cache (`pull-push`).** Any job you add later gets `pull` from `default`, so it reads the cache but doesn't spend time uploading it again.

Some things to check:

1. **There's no `package.json` or `package-lock.json` in this repo yet.** `npm ci` fails without a lockfile, so the current pipeline won't pass either until you commit one.
2. **The `test` stage has no jobs.** When you add one, it should run `npm ci --cache .npm --prefer-offline` and will use the cache automatically. If tests only need the build output, you can skip the install by passing files from `build` as `artifacts:` instead.
3. **Cache sharing depends on your runners.** Runners only share a cache if they're set up with shared storage such as S3 or GCS. Without that, each runner keeps its own local cache and the first job on each runner will still do a full download.

I haven't run this in a pipeline. `gitlab-ci-lint` or the CI Lint page in your project's GitLab settings will confirm the YAML parses before you push.
