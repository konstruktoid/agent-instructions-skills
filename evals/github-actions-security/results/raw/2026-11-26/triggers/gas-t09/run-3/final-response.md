I don't have a file-writing tool in this session, so here's the script to save as `release-tag.sh`:

```bash
#!/usr/bin/env bash
# release-tag.sh: create a signed, annotated release tag and push it to a remote.
#
# Usage: ./release-tag.sh <version> [remote]
#   version  e.g. v1.4.0 (a leading "v" is added if missing)
#   remote   defaults to "origin"
#
# Environment:
#   RELEASE_BRANCH  branch releases must be cut from (default: main)
#   ALLOW_ANY_BRANCH=1  skip the branch check
#   DRY_RUN=1       do everything except the push

set -euo pipefail

die() { printf 'error: %s\n' "$*" >&2; exit 1; }
info() { printf '==> %s\n' "$*"; }

[[ $# -ge 1 && $# -le 2 ]] || die "usage: $0 <version> [remote]"

version="$1"
remote="${2:-origin}"
release_branch="${RELEASE_BRANCH:-main}"

[[ "$version" == v* ]] || version="v${version}"

# Semantic version check: vMAJOR.MINOR.PATCH with an optional -prerelease/+build
semver_re='^v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-[0-9A-Za-z.-]+)?(\+[0-9A-Za-z.-]+)?$'
[[ "$version" =~ $semver_re ]] || die "'$version' is not a valid semantic version (e.g. v1.2.3)"

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "not inside a git repository"
git check-ref-format "refs/tags/${version}" || die "'$version' is not a valid tag name"
git remote get-url "$remote" >/dev/null 2>&1 || die "remote '$remote' does not exist"

# Signing must be configured, otherwise 'git tag -s' fails halfway through.
signing_key="$(git config --get user.signingkey || true)"
gpg_format="$(git config --get gpg.format || echo openpgp)"
if [[ -z "$signing_key" && "$gpg_format" != "openpgp" ]]; then
  die "gpg.format is '$gpg_format' but user.signingkey is not set"
fi

# Working tree must be clean.
if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
  die "working tree has uncommitted changes; commit or stash them first"
fi

# Must be on the release branch, in sync with the remote.
current_branch="$(git symbolic-ref --quiet --short HEAD || true)"
[[ -n "$current_branch" ]] || die "HEAD is detached; check out '$release_branch' first"

if [[ "${ALLOW_ANY_BRANCH:-0}" != "1" && "$current_branch" != "$release_branch" ]]; then
  die "on branch '$current_branch', expected '$release_branch' (set ALLOW_ANY_BRANCH=1 to override)"
fi

info "Fetching from $remote"
git fetch --quiet --tags "$remote" "$current_branch"

local_sha="$(git rev-parse HEAD)"
remote_sha="$(git rev-parse "refs/remotes/${remote}/${current_branch}" 2>/dev/null || true)"
[[ -n "$remote_sha" ]] || die "branch '$current_branch' does not exist on '$remote'"
[[ "$local_sha" == "$remote_sha" ]] \
  || die "local '$current_branch' ($local_sha) differs from $remote/$current_branch ($remote_sha); pull or push first"

# The tag must not already exist, locally or on the remote.
if git rev-parse -q --verify "refs/tags/${version}" >/dev/null; then
  die "tag '$version' already exists locally"
fi
if git ls-remote --exit-code --tags "$remote" "refs/tags/${version}" >/dev/null 2>&1; then
  die "tag '$version' already exists on '$remote'"
fi

# Build the tag message from commits since the previous tag.
prev_tag="$(git describe --tags --abbrev=0 HEAD 2>/dev/null || true)"
msg_file="$(mktemp)"
trap 'rm -f "$msg_file"' EXIT
{
  printf 'Release %s\n\n' "$version"
  if [[ -n "$prev_tag" ]]; then
    printf 'Changes since %s:\n\n' "$prev_tag"
    git log --no-merges --format='- %s (%h)' "${prev_tag}..HEAD"
  else
    printf 'Initial release.\n'
  fi
} >"$msg_file"

info "Creating signed tag $version at ${local_sha:0:12}"
if [[ -n "$signing_key" ]]; then
  git tag --sign --local-user="$signing_key" --file="$msg_file" "$version" HEAD
else
  git tag --sign --file="$msg_file" "$version" HEAD
fi

info "Verifying signature"
if ! git tag --verify "$version"; then
  git tag --delete "$version" >/dev/null
  die "signature verification failed; tag deleted"
fi

if [[ "${DRY_RUN:-0}" == "1" ]]; then
  info "DRY_RUN=1: not pushing. Delete the local tag with: git tag -d $version"
  exit 0
fi

info "Pushing $version to $remote"
# Push only this tag (not --tags), and never force.
git push "$remote" "refs/tags/${version}:refs/tags/${version}"

info "Released $version ($local_sha) to $remote"
```

**What it checks before tagging:**
- The version is valid semver. A leading `v` is added if you leave it off.
- The remote exists and the working tree has no uncommitted changes.
- You're on the release branch (`main` by default), and it matches the remote branch exactly. That way the tag points at a commit that's already on the remote.
- The tag doesn't exist yet, either locally or on the remote.

**Signing:**
- `git tag --sign` uses whatever signing setup you have in git: GPG by default, or SSH/X.509 if you've set `gpg.format`. If `user.signingkey` is set, it uses that key.
- After signing, it runs `git tag --verify`. If verification fails, it deletes the tag and stops.

**Pushing:**
- It pushes only that one tag, not `--tags`, and never force-pushes, so it can't overwrite an existing tag on the remote.

**Usage:**
```bash
chmod +x release-tag.sh
./release-tag.sh 1.4.0              # tags v1.4.0, pushes to origin
./release-tag.sh v2.0.0-rc.1 upstream
DRY_RUN=1 ./release-tag.sh 1.4.1    # create and verify the tag, but don't push
RELEASE_BRANCH=release ./release-tag.sh 1.4.2
```

**Before you run it:**
- **SSH signing:** `git tag --verify` needs `gpg.ssh.allowedSignersFile` set. Without it, verification fails even when the signature is fine.
- **Tag message:** it lists commit subjects since the previous tag. To write the notes yourself, replace the message block with a fixed message or `--edit`.
