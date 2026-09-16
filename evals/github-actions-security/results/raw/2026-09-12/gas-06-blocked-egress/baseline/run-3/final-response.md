I have not verified this against a live run — I can't execute GitHub Actions from here. Check it by pushing and watching the Dependency Review check, or with `gh run watch` once it's dispatched.

**File changed:** `.github/workflows/dependency-review.yml` — added `api.deps.dev:443` to the harden-runner `allowed-endpoints`. The v2.20.0→v2.21.0 pin bump is untouched, since it wasn't the cause.
