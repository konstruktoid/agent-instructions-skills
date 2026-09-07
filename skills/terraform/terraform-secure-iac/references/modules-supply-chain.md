# Module and provider supply chain

A module runs with the caller's credentials and can declare any resource. A provider is a binary
that runs on the machine planning the change. Both are code pulled from outside the repository,
and both need the pinning and review a code dependency gets.

## Pin every source

- Pin every provider in `required_providers` with a `version` constraint and a full `source`
  address including the namespace, for example `hashicorp/aws`. A bare provider name or a wrong
  namespace can resolve to a different publisher.
- Pin every module `source`. For a registry module, add a `version` constraint. For a Git module,
  append `?ref=` with a release tag or a commit SHA, never a branch name and never an omitted
  ref.
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
