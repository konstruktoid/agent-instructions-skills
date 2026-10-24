I can't create files in this session, so here's the script to save as something like `release-tag.sh`:

```bash
#!/usr/bin/env bash
#
# release-tag.sh - create a GPG/SSH-signed release tag and push it to the remote.
#
# Usage: ./release-tag.sh <version> [remote] [branch]
#   version  Semantic version, e.g. 1.2.3 or v1.2.3 (tag will be "v1.2.3")
#   remote   Remote name (default: origin)
#   branch   Branch the release must be cut from (default: main)
#
# Requires git signing to be configured (user.signingkey, and gpg.format=ssh if using SSH keys).

set -euo pipefail

die() { printf 'error: %s\n' "$*" >&2; exit 1; }

[[ $# -ge 1 ]] || die "usage: $0 <version> [remote] [branch]"

version="${1#v}"
remote="${2:-origin}"
branch="${3:-main}"
tag="v${version}"

# Validate semver (with optional pre-release/build metadata).
semver_re='^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-[0-9A-Za-z.-]+)?(\+[0-9A-Za-z.-]+)?$'
[[ $version =~ $semver_re ]] || die "'$version' is not a valid semantic version"

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "not inside a git repository"
git remote get-url "$remote" >/dev/null 2>&1 || die "remote '$remote' does not exist"
git config --get user.signingkey >/dev/null || die "user.signingkey is not set; cannot sign tag"

# Must be on the release branch with a clean working tree.
current_branch="$(git symbolic-ref --short -q HEAD || true)"
[[ $current_branch == "$branch" ]] || die "on branch '${current_branch:-detached}', expected '$branch'"
[[ -z "$(git status --porcelain)" ]] || die "working tree is not clean"

# Must be in sync with the remote branch.
git fetch --quiet --tags "$remote" "$branch"
local_sha="$(git rev-parse HEAD)"
remote_sha="$(git rev-parse "${remote}/${branch}")"
[[ $local_sha == "$remote_sha" ]] || die "local '$branch' ($local_sha) differs from ${remote}/${branch} ($remote_sha)"

# Tag must not already exist locally or on the remote.
git rev-parse -q --verify "refs/tags/${tag}" >/dev/null && die "tag '$tag' already exists locally"
if git ls-remote --exit-code --tags "$remote" "refs/tags/${tag}" >/dev/null 2>&1; then
  die "tag '$tag' already exists on '$remote'"
fi

echo "Creating signed tag ${tag} at ${local_sha:0:12}..."
git tag --sign --message "Release ${tag}" "$tag" "$local_sha"

# Verify the signature before publishing; remove the tag if verification fails.
if ! git tag --verify "$tag"; then
  git tag --delete "$tag" >/dev/null
  die "signature verification failed for '$tag'; tag removed"
fi

echo "Pushing ${tag} to ${remote}..."
git push "$remote" "refs/tags/${tag}"

echo "Released ${tag}."
```

Run it like this:

```bash
chmod +x release-tag.sh
./release-tag.sh 1.4.0                     # tags v1.4.0 from main and pushes to origin
./release-tag.sh v2.0.0-rc.1 upstream main
```

**What it does:**
- **Checks before tagging:**
  - The version has to be a valid semantic version, like `1.2.3`.
  - The remote has to exist and a signing key has to be set in git.
  - You have to be on the release branch, with no uncommitted changes.
  - Your branch has to match the remote branch exactly, so you can't tag commits that haven't been pushed and you aren't behind.
  - The tag can't already exist, either locally or on the remote.
- **Signs and verifies the tag:** It creates the tag with `git tag --sign`, then checks the signature with `git tag --verify` before pushing. If the check fails, it deletes the tag and stops.
- **Pushes only the new tag:** It uses `refs/tags/<tag>`, not `--tags` or `--follow-tags`, so other local tags don't get published by accident.

**Signing setup:** With GPG, setting `user.signingkey` is enough. To sign with an SSH key, also run `git config gpg.format ssh`. Verifying an SSH-signed tag also needs `gpg.ssh.allowedSignersFile` to be set, or the verify step will fail.
