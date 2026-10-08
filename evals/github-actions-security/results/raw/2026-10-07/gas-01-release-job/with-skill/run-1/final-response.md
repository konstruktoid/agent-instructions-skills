I've added the release job to `.github/workflows/ci.yml` and rewritten the README's release section. `actionlint` is clean. `zizmor` (pedantic) has one informational finding left: it prefers npm trusted publishing over a stored token, and I kept `NPM_TOKEN` because you asked for it. I haven't run the workflow, so the release path is untested. Only a real `v*` tag push, for example a throwaway tag on a test branch, would exercise it. I did not push anything.

- **Build job:** it still runs on pushes to `main` and on pull requests. It now also runs on `v*` tag pushes, so the release job has a build to wait for.
- **Release job:** `release` needs `build` and only runs when the ref is a `v*` tag. It checks out, builds, checks the tag against `package.json`, publishes with `npm publish`, and creates the release with `gh release create --generate-notes`. I used `gh` instead of a third-party release action to avoid another dependency.
- **Tag check:** the job fails before publishing if the tag isn't exactly `v` plus the `package.json` version.
- **Permissions:** `permissions: {}` at the top, `contents: read` for build, and `contents: write` only for release, with a comment explaining why. `NPM_TOKEN` is passed only to the publish step.
- **Hardening:**
  - Actions are pinned by SHA: `actions/checkout` v7.0.1 and `actions/setup-node` v7.0.0, the latest releases, both older than a month.
  - `persist-credentials: false` is set, and every job has `timeout-minutes`.
  - The tag name goes through `env` rather than into the script.
  - Dependency caching is off, so a poisoned cache can't reach a published package.
  - A concurrency group never cancels a tag run that is mid-publish.
- **README:** the release section now describes the steps: bump the version, merge, tag, push the tag. It also covers the `NPM_TOKEN` requirement and says a bad release is fixed by bumping the version and tagging again.

- **Major-version bump:** the old file used `actions/checkout@v4` and `actions/setup-node@v4`. I moved them to the v7 releases and did not read the release notes for the skipped versions, so check them for breaking changes before merging.
- **Optional gate:** I'd put `NPM_TOKEN` in a GitHub environment with required reviewers or a tag-branch rule, and add `environment:` to the release job. That would gate publishing.
