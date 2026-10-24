Here's a script that creates a signed annotated tag, verifies the signature, and pushes only that tag to the remote.

```bash
#!/usr/bin/env bash
# release-tag.sh — create a signed release tag and push it to the remote.
#
# Usage: ./release-tag.sh <version> [remote]
#   version  Semantic version, with or without a leading "v" (e.g. 1.4.0 or v1.4.0)
#   remote   Git remote to push to (default: origin)
#
# Environment:
#   RELEASE_BRANCH  Branch releases must be cut from (default: main)
#   TAG_MESSAGE     Tag annotation message (default: "Release <tag>")
#   DRY_RUN=1       Print what would happen without creating or pushing the tag

set -euo pipefail

die()  { printf 'error: %s\n' "$*" >&2; exit 1; }
info() { printf '==> %s\n' "$*"; }

[[ $# -ge 1 && $# -le 2 ]] || die "usage: $0 <version> [remote]"

version="${1#v}"
remote="${2:-origin}"
tag="v${version}"
release_branch="${RELEASE_BRANCH:-main}"
message="${TAG_MESSAGE:-Release ${tag}}"
dry_run="${DRY_RUN:-0}"

# Validate the version (SemVer 2.0.0, allowing pre-release and build metadata).
semver_re='^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-[0-9A-Za-z.-]+)?(\+[0-9A-Za-z.-]+)?$'
[[ $version =~ $semver_re ]] || die "'$1' is not a valid semantic version"

# Sanity checks on the repository state.
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "not inside a git repository"
git remote get-url "$remote" >/dev/null 2>&1      || die "remote '$remote' does not exist"

current_branch="$(git symbolic-ref --quiet --short HEAD || true)"
[[ $current_branch == "$release_branch" ]] \
  || die "must be on '$release_branch' (currently on '${current_branch:-detached HEAD}')"

[[ -z "$(git status --porcelain)" ]] || die "working tree is not clean; commit or stash changes first"

# Make sure signing is configured before doing anything else.
git config --get user.signingkey >/dev/null \
  || [[ "$(git config --get gpg.format || echo openpgp)" == "ssh" && -n "$(git config --get user.signingkey || true)" ]] \
  || die "no signing key configured (set user.signingkey, and gpg.format=ssh if using SSH signing)"

info "Fetching from '$remote'"
git fetch --quiet --tags "$remote" "$release_branch"

# Ensure local branch is in sync with the remote branch.
local_sha="$(git rev-parse HEAD)"
remote_sha="$(git rev-parse "${remote}/${release_branch}")"
[[ $local_sha == "$remote_sha" ]] \
  || die "local '$release_branch' ($local_sha) differs from '${remote}/${release_branch}' ($remote_sha); pull or push first"

# Refuse to overwrite an existing tag, locally or on the remote.
git rev-parse -q --verify "refs/tags/${tag}" >/dev/null && die "tag '$tag' already exists locally"
git ls-remote --exit-code --tags "$remote" "refs/tags/${tag}" >/dev/null 2>&1 \
  && die "tag '$tag' already exists on '$remote'"

if [[ $dry_run == 1 ]]; then
  info "[dry run] would create signed tag '$tag' at $local_sha and push it to '$remote'"
  exit 0
fi

info "Creating signed tag '$tag' at ${local_sha:0:12}"
git tag --sign --message "$message" "$tag"

info "Verifying tag signature"
if ! git tag --verify "$tag"; then
  git tag --delete "$tag" >/dev/null
  die "signature verification failed; tag removed"
fi

info "Pushing '$tag' to '$remote'"
git push "$remote" "refs/tags/${tag}"

info "Released $tag"
```

**Usage**

```bash
chmod +x release-tag.sh
./release-tag.sh 1.4.0                       # tags v1.4.0 and pushes it to origin
./release-tag.sh v2.0.0-rc.1 upstream        # pre-release, different remote
DRY_RUN=1 ./release-tag.sh 1.4.1             # runs the checks only, creates nothing
RELEASE_BRANCH=release ./release-tag.sh 1.4.1
```

**What it checks before tagging**
- The version is valid SemVer. The tag name is always `v<version>`.
- You're on the release branch, the working tree is clean, and your branch matches the remote branch. This stops you from tagging a commit that nobody else has.
- A signing key is configured.
- The tag doesn't already exist locally or on the remote, so it never overwrites or force-pushes a tag.

**Notes**
- `git tag --sign` uses whatever signing method you've set up. For GPG, that's just `user.signingkey`. For SSH signing, run `git config gpg.format ssh` and `git config user.signingkey ~/.ssh/id_ed25519.pub`. To verify SSH signatures you also need `gpg.ssh.allowedSignersFile`.
- If signature verification fails, the script deletes the local tag so you can fix the problem and run it again.
- It pushes only `refs/tags/<tag>`, not `--tags`, so other local tags never get pushed by accident.

I haven't run the script. Try it with `DRY_RUN=1` first.
