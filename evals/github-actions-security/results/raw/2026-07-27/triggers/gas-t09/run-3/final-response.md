The Write tool isn't available in this session, so here's the script for you to save yourself as `release-tag.sh`:

```bash
#!/usr/bin/env bash
#
# Tag a release, sign the tag with GPG, and push it to the remote.
#
# Usage: ./release-tag.sh <tag> [remote]
#   tag:    the tag name to create, e.g. v1.2.3
#   remote: the git remote to push to (default: origin)

set -euo pipefail

usage() {
    echo "Usage: $0 <tag> [remote]" >&2
    exit 1
}

[ "$#" -ge 1 ] && [ "$#" -le 2 ] || usage

tag="$1"
remote="${2:-origin}"

if [[ ! "$tag" =~ ^v[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$ ]]; then
    echo "Error: tag '$tag' does not look like a semantic version (expected vX.Y.Z)" >&2
    exit 1
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "Error: not inside a git repository" >&2
    exit 1
fi

if [ -n "$(git status --porcelain)" ]; then
    echo "Error: working tree is not clean, commit or stash changes first" >&2
    exit 1
fi

if git rev-parse "$tag" >/dev/null 2>&1; then
    echo "Error: tag '$tag' already exists" >&2
    exit 1
fi

git tag --sign --annotate "$tag" --message "Release $tag"
git push "$remote" "$tag"

echo "Tagged and pushed signed release: $tag"
```

Make it executable with `chmod +x release-tag.sh`, then run e.g. `./release-tag.sh v1.2.3`. It requires a GPG key configured for signing (`git config user.signingkey`), validates the tag format, checks for a clean working tree, and refuses to overwrite an existing tag.
