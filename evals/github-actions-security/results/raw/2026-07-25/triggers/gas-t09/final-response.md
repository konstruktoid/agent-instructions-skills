I don't have file-write or shell tools available in this session, so here's the script for you to save (e.g. as `scripts/tag-release.sh`) and `chmod +x`:

```bash
#!/usr/bin/env bash
# Tag a release, sign the tag with GPG, and push it to the remote.
#
# Usage: tag-release.sh <vX.Y.Z> [remote]

set -euo pipefail

usage() {
    echo "Usage: $0 <vX.Y.Z> [remote]" >&2
    exit 1
}

[[ $# -ge 1 && $# -le 2 ]] || usage

tag=$1
remote=${2:-origin}

if [[ ! $tag =~ ^v[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$ ]]; then
    echo "error: tag '$tag' must look like vX.Y.Z (optionally with a -prerelease suffix)" >&2
    exit 1
fi

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || {
    echo "error: not inside a git repository" >&2
    exit 1
}

if [[ -n "$(git status --porcelain)" ]]; then
    echo "error: working tree is not clean; commit or stash changes first" >&2
    exit 1
fi

if git rev-parse "$tag" >/dev/null 2>&1; then
    echo "error: tag '$tag' already exists" >&2
    exit 1
fi

if ! git config --get user.signingkey >/dev/null 2>&1; then
    echo "error: no user.signingkey configured for git; set one with 'git config user.signingkey <KEYID>'" >&2
    exit 1
fi

read -r -p "Create signed tag '$tag' at $(git rev-parse --short HEAD) and push to '$remote'? [y/N] " confirm
[[ $confirm == [yY] ]] || { echo "aborted"; exit 1; }

git tag -s "$tag" -m "Release $tag"
git push "$remote" "$tag"

echo "Pushed signed tag '$tag' to '$remote'."
```

Notes on the choices:
- `-s` creates a GPG-signed annotated tag (fails cleanly if no signing key is configured, checked up front).
- Refuses to run on a dirty working tree or over an existing tag.
- Validates the tag looks like semver (`vX.Y.Z`), and prompts for confirmation before the push since pushing a tag is hard to fully undo (others may fetch it before you can delete/retag).

Want me to write this to a file in the repo, or adjust the version format / remote defaults?
