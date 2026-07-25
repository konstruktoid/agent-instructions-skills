# Dependency and Supply Chain Hygiene

Read this when the change adds, removes, or upgrades a dependency, or touches lockfiles
and environment setup.

This maps to OWASP's Software Supply Chain Failures category (A03:2025).

## Adding a dependency

- Check whether the repository, or the standard library, already provides an equivalent
  before adding anything.
- Check a new package for typosquatting before adding it: confirm the exact name against
  the project's own documentation or repository, not against search results.
- Look at the package's maintenance state (recent releases, open advisories) rather than
  download count alone.

## Pinning and environments

- Pin dependencies through a lockfile, and commit it.
- Use an isolated virtual environment rather than system Python.

## Vulnerability scanning

- Run the repository's existing dependency vulnerability scanner (`pip-audit`,
  `uv audit`, Snyk, or similar). Do not add a second scanner alongside one that is
  already configured.
- `uv audit` (uv 0.10.12 and later) is a fast, uv-native alternative to `pip-audit`, but
  it is still a preview feature with an unstable interface. Do not introduce it into a
  repository that already relies on `pip-audit` or another scanner without asking first.
- If no scanner is configured, report what a one-off scan found rather than silently
  adding a scanner to the project's configuration.
