I don't have a file-writing tool in this session, so here's the script to save as `release-tag.sh`:

```bash
#!/usr/bin/env bash
# Create a signed, annotated release tag and push it to the remote.
#
# Usage: release-tag.sh <version> [message]
#   version  Semantic version, with or without a leading "v" (e.g. 1.4.0 or v1.4.0)
#   message  Tag message (default: "Release v<version>")
#
# Environment:
#   REMOTE          Remote to push to (default: origin)
#   RELEASE_BRANCH  Branch the tag must be created from (default: main)
#   DRY_RUN=1       Run every check but skip creating and pushing the tag
#
# Signing follows your git config, so it works with both GPG and SSH keys:
#   git config user.signingkey <key-id or path to SSH public key>
#   git config gpg.format ssh      # only if you sign with SSH

set -euo pipefail

REMOTE="${REMOTE:-origin}"
RELEASE_BRANCH="${RELEASE_BRANCH:-main}"
DRY_RUN="${DRY_RUN:-0}"

die()  { printf 'error: %s\n' "$*" >&2; exit 1; }
info() { printf '==> %s\n' "$*"; }

usage() {
  sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'
  exit "${1:-0}"
}

[[ $# -ge 1 && $# -le 2 ]] || usage 1
[[ "$1" == "-h" || "$1" == "--help" ]] && usage 0

version="${1#v}"
tag="v${version}"
message="${2:-Release ${tag}}"

# Semantic version check (allows pre-release and build metadata, e.g. 1.2.3-rc.1+build.5).
semver_re='^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-[0-9A-Za-z.-]+)?(\+[0-9A-Za-z.-]+)?$'
[[ "$version" =~ $semver_re ]] || die "'$1' is not a valid semantic version"

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "not inside a git repository"
git remote get-url "$REMOTE" >/dev/null 2>&1 || die "remote '$REMOTE' does not exist"

# A signing key must be configured, or 'git tag -s' falls back to guessing from user.email.
git config --get user.signingkey >/dev/null || die "no signing key set (git config user.signingkey)"

# Must be on the release branch.
current_branch="$(git symbolic-ref --quiet --short HEAD)" || die "HEAD is detached"
[[ "$current_branch" == "$RELEASE_BRANCH" ]] \
  || die "on branch '$current_branch', expected '$RELEASE_BRANCH'"

# Working tree must be clean (tracked and untracked files).
[[ -z "$(git status --porcelain)" ]] || die "working tree has uncommitted or untracked changes"

# Local branch must match the remote exactly, so the tag points at a published commit.
info "Fetching from $REMOTE"
git fetch --quiet --tags "$REMOTE" "$RELEASE_BRANCH"
local_sha="$(git rev-parse HEAD)"
remote_sha="$(git rev-parse "$REMOTE/$RELEASE_BRANCH")"
[[ "$local_sha" == "$remote_sha" ]] \
  || die "local $RELEASE_BRANCH ($local_sha) differs from $REMOTE/$RELEASE_BRANCH ($remote_sha); push or pull first"

# The tag must not exist locally or on the remote.
git rev-parse -q --verify "refs/tags/$tag" >/dev/null && die "tag '$tag' already exists locally"
if git ls-remote --exit-code --tags "$REMOTE" "refs/tags/$tag" >/dev/null 2>&1; then
  die "tag '$tag' already exists on $REMOTE"
fi

info "Tagging $local_sha as $tag"
if [[ "$DRY_RUN" == "1" ]]; then
  info "DRY_RUN=1: all checks passed; tag not created or pushed"
  exit 0
fi

git tag --sign --annotate --message "$message" "$tag" "$local_sha"

# Check the signature before anything leaves the machine; remove the tag if it fails.
if ! git tag --verify "$tag" >/dev/null 2>&1; then
  git tag --delete "$tag" >/dev/null
  die "signature verification failed for '$tag'; tag deleted"
fi
info "Signature verified"

# Push only this tag (not --tags, which would push every local tag).
info "Pushing $tag to $REMOTE"
git push --atomic "$REMOTE" "refs/tags/$tag"

info "Released $tag ($local_sha)"
```

To use it:

```bash
chmod +x release-tag.sh
DRY_RUN=1 ./release-tag.sh 1.4.0     # run the checks only
./release-tag.sh 1.4.0 "Release v1.4.0: add widget support"
```

**What it checks before tagging:**
- The version is valid semver. A leading `v` is optional, and the tag is always written as `v<version>`.
- You're on the release branch, it has no uncommitted or untracked changes, and it matches the remote exactly. That way the tag points at a commit that's already published.
- The tag doesn't exist yet, either locally or on the remote.
- A signing key is set in your git config.

**Signing:** it uses `git tag -s`, so it follows your git config and works with GPG or SSH keys. It checks the signature with `git tag --verify` before pushing. If that check fails, it deletes the local tag so nothing unsigned gets pushed. To verify SSH signatures, you also need `gpg.ssh.allowedSignersFile` set.

**Pushing:** it pushes only the new tag (`refs/tags/vX.Y.Z`), not `--tags`, so other local tags you might have lying around don't get published by accident.

**Settings:** use `REMOTE` and `RELEASE_BRANCH` if your remote isn't `origin` or your branch isn't `main`.

I haven't run the script. A good first step is `DRY_RUN=1`, which runs every check but doesn't create or push the tag. Note that the dry run stops before signing, so it won't catch a broken signing setup.
