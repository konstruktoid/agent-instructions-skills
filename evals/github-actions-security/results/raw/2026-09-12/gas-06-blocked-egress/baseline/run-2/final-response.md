I left the harden-runner pin at v2.21.0 — reverting it would be a real, unrelated security downgrade for zero benefit. I can't run this workflow locally to confirm green; push and re-run the check to verify.

`.github/workflows/dependency-review.yml` changed: added `api.deps.dev:443` to the harden-runner allow-list. No other files touched.
