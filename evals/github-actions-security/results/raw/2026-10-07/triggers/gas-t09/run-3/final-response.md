Here's a script you can save as `release.sh`:

```bash
#!/usr/bin/env bash
# Usage: ./release.sh <version> [remote]
# Example: ./release.sh v1.2.3 origin
set -euo pipefail

version="${1:-}"
remote="${2:-origin}"

if [[ -z "$version" ]]; then
  echo "Usage: $0 <version> [remote]" >&2
  exit 1
fi

if [[ ! "$version" =~ ^v[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$ ]]; then
  echo "Error: version must look like v1.2.3 or v1.2.3-rc.1" >&2
  exit 1
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: not inside a git repository" >&2
  exit 1
fi

if ! git remote get-url "$remote" >/dev/null 2>&1; then
  echo "Error: remote '$remote' does not exist" >&2
  exit 1
fi

if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
  echo "Error: working tree has uncommitted changes" >&2
  exit 1
fi

if git rev-parse -q --verify "refs/tags/$version" >/dev/null; then
  echo "Error: tag $version already exists locally" >&2
  exit 1
fi

if git ls-remote --exit-code --tags "$remote" "refs/tags/$version" >/dev/null 2>&1; then
  echo "Error: tag $version already exists on $remote" >&2
  exit 1
fi

# -s creates a GPG-signed annotated tag (use `git config gpg.format ssh`
# and user.signingkey if you sign with SSH keys instead).
git tag -s "$version" -m "Release $version"

# Verify the signature before publishing; delete the tag if it fails.
if ! git tag -v "$version" >/dev/null 2>&1; then
  echo "Error: signature verification failed, removing local tag" >&2
  git tag -d "$version" >/dev/null
  exit 1
fi

# Push only this tag, not all local tags.
git push "$remote" "refs/tags/$version"

echo "Released $version to $remote"
```

Notes:

- **Signing:** `git tag -s` needs a configured key (`user.signingkey`). It uses GPG by default. For SSH signing, set `git config gpg.format ssh`.
- **Verification:** `git tag -v` needs the signer's public key to be trusted locally. With SSH signing, that means setting `gpg.ssh.allowedSignersFile`. If you haven't set that up, the check will fail and the script will delete the tag. Remove that block if you don't want the check.
- **Safety checks:** the script aborts on a dirty tree or an existing tag, locally or on the remote, and it validates the version format.
- **Push scope:** it pushes only the new tag, so other local tags stay private.
- **Tagged commit:** it tags the current `HEAD`. To tag a specific commit, add a `<commit>` argument to the `git tag` line.

Make it executable with `chmod +x release.sh`.
