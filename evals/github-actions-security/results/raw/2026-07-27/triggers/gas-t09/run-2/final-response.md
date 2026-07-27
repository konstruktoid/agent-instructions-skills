I don't have file-write tools available in this session, so here's the script — save it as `release.sh` and `chmod +x` it:

```bash
#!/usr/bin/env bash
set -euo pipefail

usage() {
    echo "Usage: $0 <tag> [message]" >&2
    echo "  <tag>      Tag name, e.g. v1.2.3" >&2
    echo "  [message]  Annotation message (default: 'Release <tag>')" >&2
    exit 1
}

[ $# -ge 1 ] || usage

TAG="$1"
MESSAGE="${2:-Release ${TAG}}"
REMOTE="${REMOTE:-origin}"

if ! git rev-parse --git-dir >/dev/null 2>&1; then
    echo "Error: not inside a git repository" >&2
    exit 1
fi

if [[ ! "$TAG" =~ ^v?[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$ ]]; then
    echo "Error: '$TAG' doesn't look like a semantic version (e.g. v1.2.3)" >&2
    exit 1
fi

if git rev-parse "$TAG" >/dev/null 2>&1; then
    echo "Error: tag '$TAG' already exists" >&2
    exit 1
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "Error: working tree has uncommitted changes" >&2
    exit 1
fi

echo "Creating signed tag '$TAG'..."
git tag -s "$TAG" -m "$MESSAGE"

echo "Verifying signature..."
git tag -v "$TAG"

read -rp "Push tag '$TAG' to '$REMOTE'? [y/N] " confirm
if [[ "$confirm" =~ ^[Yy]$ ]]; then
    git push "$REMOTE" "$TAG"
    echo "Pushed $TAG to $REMOTE."
else
    echo "Tag created locally but not pushed. Run: git push $REMOTE $TAG"
fi
```

Notes:
- Requires a GPG (or SSH, with `git config gpg.format ssh`) signing key already configured via `user.signingkey`.
- Refuses to run with uncommitted changes or a pre-existing tag, and validates the tag looks like a semver string.
- Confirms before pushing since pushing a tag is visible to others and not easily undone.

Want me to actually create this file in a project once you point me at one, or adjust anything (e.g., skip the confirmation prompt for CI use)?
