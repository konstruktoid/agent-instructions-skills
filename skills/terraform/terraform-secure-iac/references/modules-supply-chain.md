# Module and provider supply chain

A module runs with the caller's credentials and can declare any resource. A provider is a binary
that runs on the machine planning the change. Both are code pulled from outside the repository,
and both need the pinning and review a code dependency gets.

## Pin every source

- Pin every provider in `required_providers` with a `version` constraint and a full `source`
  address including the namespace, for example `hashicorp/aws`. A bare provider name or a wrong
  namespace can resolve to a different publisher.
- Pin every module `source` to an immutable revision. For a registry module, set an exact
  `version`, not a range: a range can resolve to a newer module on the next `init`. For a Git
  module, append `?ref=` with a full commit SHA, or with a release tag that the source repository
  protects against being moved; never a branch name, a plain movable tag, or an omitted ref.
- Use HTTPS or SSH transport for a remote module `source`. Terraform also accepts `http` and
  `ftp` Git URLs, which a `ref` pin does not make safe. Put no credentials in the URL, and keep
  remote module hosts to a known set.
- Set `required_version` for Terraform itself.

## The dependency lock file

- Commit `.terraform.lock.hcl`. It records the exact provider versions and their checksums, so
  every run and every developer resolves the same binaries.
- Run `terraform providers lock -platform=` for each operating system and architecture that CI
  and developers use, so the lock file carries a checksum for all of them. A lock file with only
  one platform's hashes breaks `init` on the others or skips verification.
- Review a lock file change like any other dependency bump: check which provider moved, to what
  version, and why.

## Review third-party modules

- Read a third-party module before adopting it. It can declare resources beyond its stated
  purpose, run provisioners, and read data sources that move values out through its outputs.
- Prefer a small number of reviewed internal modules, published to an internal registry, over
  many public sources. Mirror a public module into the internal registry rather than sourcing it
  from its origin on every run.
- Re-review on upgrade. A pinned module that moves to a new version is new code.

## Upgrades

- Upgrade providers and modules deliberately, one at a time where possible. Read the changelog
  for default changes and forced replacements.
- Run the upgrade against a non-production root first and read the resulting plan before
  promoting it.
