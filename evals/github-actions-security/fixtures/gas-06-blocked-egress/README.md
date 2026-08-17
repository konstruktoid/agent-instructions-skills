# widget

A small Python package. CI runs the test suite on every pull request, and a separate Dependency
Review check inspects dependency changes.

Both workflows start with `step-security/harden-runner`. The Dependency Review job runs it in
`block` mode against an explicit allowlist; the CI job runs it in `audit` mode.

`ci-logs/` holds two saved job logs from the Dependency Review check, one failing and one passing,
kept for the investigation described in the open pull request.
