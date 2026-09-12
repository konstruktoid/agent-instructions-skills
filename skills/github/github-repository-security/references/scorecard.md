# OpenSSF Scorecard

Read this when a repository is graded by OpenSSF Scorecard, when a specific check scores low, or
when the goal is stated as raising the Scorecard result. Scorecard grades a repository from
outside its own claims, so a low check is evidence that a control this skill configures is absent,
not in force, or not visible to an external reader.

## Contents

- What the score measures
- Running the check
- The check map
- Branch-Protection: the tier ladder
- Code-Review reads history, not configuration
- Signed-Releases and Packaging need real releases
- Pinned-Dependencies covers the whole tree
- CII Best Practices badge
- Checks configuration cannot move
- Checklist

## What the score measures

Each check returns a score from 0 to 10, or -1 when it could not run, and the overall score is a
weighted average. A check reports one of three things: a control is present and configured, a
control is present but weaker than the top tier, or a control is absent. The remedy for a low
check is the mechanism the rest of this skill already describes. This file maps each check to that
mechanism and records the tier thresholds, since several checks award partial credit and the
difference between 6 and 10 is a specific setting rather than a category of effort.

Raising a check that reads repository history, Code-Review and Contributors and Maintained, takes
effect over weeks of merged pull requests rather than at the moment a setting changes. Enforce the
mechanism now and the score follows as history accumulates under it.

## Running the check

Resolve the current Scorecard release rather than recalling a version. Run it against the
repository with a token that can read repository administration, and record which version ran:

```sh
gh api repos/ossf/scorecard/releases/latest --jq .tag_name
SCORECARD_TAG=$(gh api repos/ossf/scorecard/releases/latest --jq .tag_name)
docker run --rm -e GITHUB_TOKEN \
  "gcr.io/openssf/scorecard:${SCORECARD_TAG}" \
  --repo="github.com/OWNER/REPO" --show-details
```

Pin the container by digest in any automated use, for the reason every other pinned dependency in
this library is pinned by digest. The hosted result at `api.securityscorecards.dev` is refreshed
on a schedule and lags a configuration change by up to a week.

## The check map

| Check | Mechanism | Reference | What Scorecard looks for |
|---|---|---|---|
| Branch-Protection | Default-branch ruleset, review rules, admin inclusion | [rulesets.md](rulesets.md) | Force-push and deletion blocked, pull request required, status check required, two reviewers, code-owner review, stale dismissal, no administrator bypass |
| Code-Review | Enforced approvals with no bypass merges | [rulesets.md](rulesets.md) | Approval recorded on recent changesets, or a merger distinct from the committer |
| Token-Permissions | `permissions: {}` at workflow level, job-scoped writes | github-actions-security supply-chain.md | Read-only top-level token, write scopes only at job level |
| Pinned-Dependencies | SHA-pinned actions, digest-pinned images, committed lock files | [supply-chain.md](../../github-actions-security/references/supply-chain.md) | Hashes rather than mutable tags across workflows, Dockerfiles, and package manifests |
| Dangerous-Workflow | No fork code under `pull_request_target`, no script injection | github-actions-security untrusted-input.md | Absence of untrusted checkout and untrusted interpolation into `run:` |
| Dependency-Update-Tool | Dependabot or Renovate configuration | [scanning-and-response.md](scanning-and-response.md) | A recognized update-tool config file |
| SAST | CodeQL in a workflow, or a SAST app on recent pull requests | [scanning-and-response.md](scanning-and-response.md) | `github/codeql-action` in a workflow, or CodeQL and SonarCloud results |
| Security-Policy | `SECURITY.md` with a reporting channel and a process | [scanning-and-response.md](scanning-and-response.md) | A policy file in a known location, a contact link, and disclosure text |
| Signed-Releases | Signature or SLSA provenance asset on every recent release | [releases-and-provenance.md](releases-and-provenance.md) | `*.sig`, `*.asc`, `*.sigstore.json`, or `*.intoto.jsonl` on each of the last five releases |
| Packaging | A workflow that publishes to a package registry | [releases-and-provenance.md](releases-and-provenance.md) | A recognized publish action or a GitHub Packages publish step |
| CII-Best-Practices | OpenSSF Best Practices Badge | this file | A passing, silver, or gold badge for the project |
| Vulnerabilities | No open advisories with a fix available | [scanning-and-response.md](scanning-and-response.md) | OSV reports no known unfixed vulnerability |
| License | A license file in a standard location | this file | `LICENSE`, `COPYING`, or a `LICENSES/` directory with an OSI or FSF license |
| Binary-Artifacts | No executables committed to the tree | [agent-content.md](agent-content.md) | No binary artifact in the repository |
| CI-Tests | Status checks run on merged pull requests | [rulesets.md](rulesets.md) | A check run associated with recent merged pull requests |
| Fuzzing | OSS-Fuzz, ClusterFuzzLite, or native fuzz targets | this file | The project in the OSS-Fuzz list, a ClusterFuzzLite workflow, or fuzz functions |
| Maintained | Commit and issue activity over 90 days | this file | At least one commit most weeks in the last 90 days, and the project older than 90 days |
| Contributors | Commits from several organizations | this file | Contributors from at least three companies across the last 30 commits |

## Branch-Protection: the tier ladder

Scorecard scores this check in cumulative tiers. Each tier is worth reaching because the points
are additive and the higher tiers are single ruleset fields, not a different class of work. The
rules below are ruleset rules on the default branch; see [rulesets.md](rulesets.md) for the JSON.

| Tier | Score | Rules it adds |
|---|---|---|
| 1 | 3 | Block force pushes, block branch deletion |
| 2 | 6 | Require a pull request before merging, require the branch up to date, require approval of the most recent reviewable push, and apply all of this to administrators |
| 3 | 8 | Require at least one status check to pass before merging |
| 4 | 9 | Require at least two approving reviews, require review from code owners |
| 5 | 10 | Dismiss stale approvals when new commits are pushed, and include administrators in the review requirement rather than granting them a bypass |

Two ruleset details decide whether tier 2 and tier 5 register:

- **No bypass actor on the default-branch ruleset.** Scorecard reads an administrator bypass as
  the protection not applying to administrators, which caps the check below tier 5. Where a
  single-maintainer repository needs a bypass to merge at all, that is a deliberate exception with
  the cost stated: the check will not reach 10.
- **The ruleset is `active`, not `evaluate`.** An evaluate-mode ruleset blocks nothing and scores
  nothing.

## Code-Review reads history, not configuration

This check inspects recent merged changesets for evidence of review: a recorded approval, or a
merger different from the committer. A repository that enables the review rule today still scores
low until reviewed pull requests accumulate in its history. An unreviewed human change is the
heaviest deduction in the check.

- Require at least one approving review through the default-branch ruleset, and apply it to
  administrators, so a direct push by a maintainer cannot bypass the record.
- Route every change through a pull request, including a maintainer's own and a bot's. A commit
  pushed straight to the default branch is an unreviewed changeset to this check.
- Dependabot and other bot pull requests count as reviewed only when a human approves them before
  merge, or an automerge rule records an approval. Left to merge themselves, they are unreviewed
  bot changesets and deduct from the score.

## Signed-Releases and Packaging need real releases

Both checks return -1 when the repository has published no GitHub release. The first release
raises them from "could not run" into a real score, so cut releases from the protected tag as
[releases-and-provenance.md](releases-and-provenance.md) describes.

- **Signed-Releases reaches 8** when every one of the last five releases carries a signature asset
  (`*.sig`, `*.asc`, `*.minisig`, `*.sigstore.json`, and similar), and **10** when every release
  carries a SLSA provenance file (`*.intoto.jsonl`). Generate the provenance in the publishing job
  with `actions/attest-build-provenance` and attach the returned file to the release.
- **Packaging** is satisfied by a workflow that publishes to a package registry: a language hub
  such as PyPI, npm, or crates.io through a recognized publish action, or GitHub Packages. For a
  repository that ships to a non-code hub, such as an Ansible role publishing to Ansible Galaxy,
  the galaxy import step on a tag push is what the check recognizes. Keep the publishing job
  separate from any job that builds or tests contributed code.

## Pinned-Dependencies covers the whole tree

Scorecard's pinning check is not limited to `uses:` lines. It reads every dependency declaration
it can find and scores the fraction pinned to a hash or a full version:

- **GitHub Actions**: pinned only by a full 40-character commit SHA. A tag is unpinned.
- **Container images**: `FROM image@sha256:...` in every Dockerfile the repository ships, including
  those inside composite actions.
- **Package manifests**: a committed lock file (`package-lock.json`, `uv.lock`, `poetry.lock`,
  `Gemfile.lock`, `go.sum`) so the resolved versions are recorded. A full semantic version for a
  Go module counts as pinned without a separate hash.
- **Scripted downloads**: a `curl` or `wget` in a workflow `run:` block or a shipped script that
  pipes a remote file into a shell, or installs from a release URL, without verifying a checksum.

See [supply-chain.md](../../github-actions-security/references/supply-chain.md) for the pinning
procedure and the tools that apply it across a repository.

## CII Best Practices badge

The CII-Best-Practices check scores the project's OpenSSF Best Practices Badge: 2 for in progress,
5 for passing, 7 for silver, 10 for gold. Enroll the project at the Best Practices site, answer
the questionnaire against the controls already configured, and add the badge to the repository
`README`. Most of the passing-level criteria, a reporting channel, a public repository, a test
suite, static analysis, and a stated contribution process, are already met by a repository that
satisfies this skill's baseline, so the gap is the enrollment rather than new engineering.

## Checks configuration cannot move

State these plainly rather than reporting them as failures a change will fix:

- **Maintained** requires the project to be older than 90 days and to show roughly weekly commit
  or issue activity across that window. A new repository scores 0 until it ages, and no
  configuration changes that.
- **Contributors** requires commits from at least three organizations across the last 30 commits.
  It measures the contributor base, not a setting.
- **Fuzzing** is satisfied by OSS-Fuzz integration, a ClusterFuzzLite workflow, or native fuzz
  targets. A repository that ships only configuration, such as an Ansible role or a Terraform
  module, has no code path to fuzz; record the check as not applicable rather than pursuing it.

## Checklist

- [ ] Scorecard run at a resolved version, recorded, with the per-check detail read
- [ ] Default-branch ruleset `active`, blocking force push and deletion, requiring a pull request,
      a status check, two approvals, and code-owner review, with stale dismissal on
- [ ] No bypass actor on the default-branch ruleset, or the exception and its score cost stated
- [ ] Every change, including maintainer and bot commits, routed through a pull request
- [ ] At least one release published, cut from the protected tag
- [ ] Each recent release carries a signature asset, or a `*.intoto.jsonl` provenance file for the
      full score
- [ ] A workflow publishes the package to a registry the Packaging check recognizes
- [ ] Actions, container images, lock files, and scripted downloads pinned across the whole tree
- [ ] OpenSSF Best Practices Badge enrolled and its mark added to the `README`
- [ ] Checks that configuration cannot move, Maintained, Contributors, and Fuzzing where it does
      not apply, reported as such rather than as open work
