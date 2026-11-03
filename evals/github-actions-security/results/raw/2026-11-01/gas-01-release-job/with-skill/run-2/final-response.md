I added the release job to `.github/workflows/ci.yml` and rewrote the README's release section. I haven't run the workflow, and I haven't pushed anything.

- **Triggers:** the workflow now also runs on pushed `v*` tags. The `build` job still runs on pushes to `main` and on pull requests, and it runs on tags too.
- **Two jobs instead of one:**
  - `release` needs `build`, builds the package and runs `npm publish` with `NPM_TOKEN`. It only has read access to the repo.
  - `github-release` needs `release` and runs `gh release create` with generated notes. It's the only job with write access (`contents: write`). This keeps the write token away from the build scripts that run during publish.
- **Tag check:** `release` fails if the tag isn't `v` plus the exact `package.json` version.
- **Hardening:**
  - Actions are pinned to commit SHAs from the current releases: checkout v7.0.1 and setup-node v7.1.0. Both are older than a week.
  - Workflow permissions are empty by default.
  - Credentials aren't persisted, jobs have timeouts, and dependency caching is off (including in `build`, since it now runs on tags).
  - Concurrency never cancels a tag run.
- **README:** the release section now describes the process: bump the version, merge, push the tag, then build, publish and release run in order.

`actionlint` is clean. `zizmor` (pedantic) has one remaining informational finding. It prefers npm trusted publishing (OIDC) over a stored token, but you asked for `NPM_TOKEN`, so I kept it. Switching later would also let you publish with provenance.

Two things I didn't check:
- Whether the `NPM_TOKEN` secret exists in the repo.
- Whether the workflow actually runs. That would take a real tag push, which would publish a version to npm, so I'd want your go-ahead first.

You could also put the secret in a protected GitHub environment with required reviewers. That would add an approval gate before publishing.
