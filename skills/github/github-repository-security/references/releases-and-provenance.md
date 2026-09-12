# Releases, Tags, and Provenance

Read this when configuring how a repository publishes releases, protecting the tags releases are
cut from, or establishing that an artifact came from the source it claims.

## Contents

- The release is the supply chain boundary
- Protect the tag
- Publish from a tag, not from a branch
- Trusted publishing with OIDC
- Immutable releases
- Signing commits and tags
- Build provenance and attestations
- Signed releases and packaging as an external check
- What a consumer can verify
- Checklist

## The release is the supply chain boundary

Everything before a release is the project's own risk. Everything after it is the risk of everyone
who installs the artifact. The controls in this file exist so that a consumer can answer one
question without trusting anyone: does this artifact correspond to the reviewed source at the
version it claims?

## Protect the tag

A release tag is the name a consumer pins to. If the tag can move, the pin is decorative:

- Add a tag ruleset covering the release pattern, blocking deletion and force update.
- Restrict tag creation on that pattern to the roles that publish releases.
- Keep the release pattern narrow. A ruleset targeting `v*` protects releases; one targeting `*`
  also blocks the throwaway tags people use while working.

## Publish from a tag, not from a branch

A release triggered by a push to a branch publishes whatever the branch held at that moment, which
is not a reviewable artifact. Trigger publication on a tag matching the protected pattern, check
out that exact tag, and let the job fail rather than fall back to the default branch when the tag
is missing.

Keep the publishing job separate from the job that builds or tests contributed code, so the
publishing credential is never present while untrusted code runs.

## Trusted publishing with OIDC

A long-lived registry token stored as a repository secret is the credential most worth removing.
Trusted publishing replaces it: the registry trusts the repository, the workflow, and the
environment, and the job exchanges a short-lived OIDC token for publish access. Nothing durable is
stored, so nothing durable can leak.

- Configure the trust condition on an exact claim: the repository, the workflow file, and the
  environment. A wildcard in the trust condition gives away the property that makes it safer than
  a token.
- Where the registry does not support it, keep the token in an environment gated by required
  reviewers, restricted to the release branch or tag pattern, and rotate it on a schedule.

## Immutable releases

Immutable releases prevent a published release's tag and assets from being changed after
publication, and generate a single release attestation binding the release tag, the commit SHA,
and the set of assets. Enable the setting before the first release that matters, since it applies
to releases published afterwards.

That is a release-level claim, and a different one from the per-artifact provenance a workflow
produces with `actions/attest-build-provenance`, which says how a given file was built. A release
can carry both, and a consumer verifying only the release attestation has checked what was
published rather than how it was built.

It narrows the window rather than closing it. The protection covers the release's own tag, so a
moving major or minor tag that no release owns stays mutable. A consumer pinning to a moving tag
is still trusting the publisher's account security.

## Signing commits and tags

Commit signing establishes that a commit came from a key the author controls, which is a different
claim from the account that pushed it. Require signed commits once adoption is wide enough that
the rule does not simply generate exceptions, and sign release tags in every case, since a signed
tag is the artifact a consumer can check without cloning the history.

## Build provenance and attestations

An attestation records which workflow, in which repository, at which commit, produced an artifact.
Generate one in the publishing job, and publish it alongside the artifact.

The value appears at the consumer's end: given an artifact and an attestation, the consumer
verifies the source repository and workflow rather than trusting the file name. Publishing an
attestation nobody verifies still helps, since it makes verification possible later without
republishing.

## Signed releases and packaging as an external check

OpenSSF Scorecard grades two release properties from outside the repository, and both return -1,
meaning the check could not run, until the repository has published its first GitHub release. The
first release cut from the protected tag turns both into a real score.

- **Signed-Releases** reaches 8 when every one of the last five releases carries a signature asset,
  matched by extension: `*.sig`, `*.asc`, `*.minisig`, `*.sigstore.json`, and similar. It reaches
  10 when every release carries a SLSA provenance file, `*.intoto.jsonl`. The provenance from
  `actions/attest-build-provenance` satisfies the top tier: write the returned file into the
  release assets in the publishing job.
- **Packaging** is satisfied by a workflow that publishes to a package registry: a language hub
  through a recognized publish action, or GitHub Packages. A repository publishing to a non-code
  hub, such as an Ansible role importing to Ansible Galaxy on a tag push, is recognized by that
  publish step. Keep the step in the release workflow rather than a manual process, since the
  check reads the workflow.

Neither raises a score on its own until releases exist and recur, so a repository that never tags
a release scores nothing on either however well the publishing job is written.

## What a consumer can verify

State in the repository's own documentation which of these a consumer can check, since a claim
that cannot be checked is not a control:

- The tag is protected and the release is immutable, so the version cannot be repointed.
- The artifact carries an attestation naming the source repository, workflow, and commit.
- The release was published by a workflow using trusted publishing rather than a stored token.
- The tag is signed by a key the project publishes.

A consumer installing agent-facing content pins to a tag rather than a default branch, which is
only meaningful when the tag is protected. Publishing that instruction without the tag ruleset
behind it is advice the repository does not honor.

## Checklist

- [ ] Release tag pattern protected against deletion and force update, with creation restricted
- [ ] Publication triggered by a tag matching the protected pattern, checking out that exact tag
- [ ] Publishing job separate from any job that builds or tests contributed code
- [ ] Trusted publishing with OIDC in use, or the stored token gated by an environment with
      required reviewers and a rotation schedule
- [ ] OIDC trust condition matched on exact claims, with no wildcard
- [ ] Immutable releases enabled where the platform supports it
- [ ] Release tags signed, and commit signing required where adoption allows
- [ ] An attestation generated and published with each artifact
- [ ] At least one release published, so the external signed-release and packaging checks can run
- [ ] Each of the last five releases carries a signature asset, or a `*.intoto.jsonl` provenance
      file for the full external score
- [ ] A publish step in the release workflow sends the package to a registry the external
      packaging check recognizes
- [ ] The repository documents what a consumer can verify, and every claim in it is checkable
