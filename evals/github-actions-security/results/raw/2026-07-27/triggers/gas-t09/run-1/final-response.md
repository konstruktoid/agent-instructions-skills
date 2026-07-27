The Write tool isn't enabled in this session, so I can't create the file directly — here's the script to save as `scripts/tag-release.sh`:

```bash
#!/usr/bin/env bash
#
# Tag a release, sign the tag with GPG, and push it to the remote.
#
# Usage: scripts/tag-release.sh <version> [remote]
# Example: scripts/tag-release.sh v1.4.0 origin

set -euo pipefail

version="${1:?Usage: $0 <version> [remote]}"
remote="${2:-origin}"

if [[ ! "$version" =~ ^v[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$ ]]; then
  echo "error: version must look like vMAJOR.MINOR.PATCH (got: $version)" >&2
  exit 1
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "error: working tree has uncommitted changes, aborting" >&2
  exit 1
fi

if git rev-parse "$version" >/dev/null 2>&1; then
  echo "error: tag $version already exists" >&2
  exit 1
fi

git tag --sign --message "Release $version" "$version"
git push "$remote" "$version"

echo "Tagged and pushed $version to $remote"
```

Make it executable with `chmod +x scripts/tag-release.sh`. It requires a GPG signing key configured for git (`user.signingkey` / `git config --global commit.gpgsign` setup); `git tag --sign` will fail with a clear error otherwise. Run it as `scripts/tag-release.sh v1.4.0`.
