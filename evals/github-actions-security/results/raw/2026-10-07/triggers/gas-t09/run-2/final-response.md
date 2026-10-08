This script tags a release, signs the tag, and pushes it. I haven't run it, because I can't execute commands in this session.

```bash
#!/usr/bin/env bash
# Usage: release.sh <version> [remote]
# Example: release.sh v1.2.3 origin
set -euo pipefail

version="${1:-}"
remote="${2:-origin}"

if [[ -z "$version" ]]; then
  echo "usage: $0 <version> [remote]" >&2
  exit 64
fi

# Require a semver-style tag, e.g. v1.2.3 or v1.2.3-rc.1
if [[ ! "$version" =~ ^v[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$ ]]; then
  echo "error: version must look like v1.2.3 (got '$version')" >&2
  exit 64
fi

# Refuse to release from a dirty working tree
if [[ -n "$(git status --porcelain)" ]]; then
  echo "error: working tree has uncommitted changes" >&2
  exit 1
fi

# Refuse to overwrite an existing tag, locally or on the remote
if git rev-parse -q --verify "refs/tags/$version" >/dev/null; then
  echo "error: tag $version already exists locally" >&2
  exit 1
fi
if git ls-remote --exit-code --tags "$remote" "refs/tags/$version" >/dev/null 2>&1; then
  echo "error: tag $version already exists on $remote" >&2
  exit 1
fi

# Make sure we are tagging what the remote has (no unpushed or unpulled commits)
branch="$(git symbolic-ref --short HEAD)"
git fetch --quiet "$remote" "$branch"
if [[ "$(git rev-parse HEAD)" != "$(git rev-parse "$remote/$branch")" ]]; then
  echo "error: HEAD differs from $remote/$branch; push or pull first" >&2
  exit 1
fi

# -s creates a GPG/SSH-signed annotated tag (uses user.signingkey / gpg.format)
git tag -s "$version" -m "Release $version"

# Verify the signature before publishing
git tag -v "$version"

# Push only this tag, not all local tags
git push "$remote" "refs/tags/$version"

echo "Released $version to $remote"
```

What it does:
- **Checks first:** it validates the version format and requires a clean working tree. It also refuses to reuse a tag that already exists locally or on the remote, and it requires `HEAD` to match the remote branch.
- **Signing:** `git tag -s` makes a signed, annotated tag. It uses your configured `user.signingkey`. For SSH signing, set `gpg.format=ssh`.
- **Verification:** `git tag -v` runs before the push. If the signature doesn't verify, `set -e` stops the script before anything is published.
- **Push:** it pushes only the new tag, not every local tag.

To use it, save it as `release.sh`, run `chmod +x release.sh`, then run `./release.sh v1.2.3`.
