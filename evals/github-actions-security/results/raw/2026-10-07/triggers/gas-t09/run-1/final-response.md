I couldn't save this as a file because the Write tool is disabled in this session. Here is the script. Save it as `release.sh` and run `chmod +x release.sh`.

```bash
#!/usr/bin/env bash
# Tag a release, sign the tag, and push it to the remote.
#
# Usage: ./release.sh <version> [remote]
#   version  tag name, e.g. v1.2.3
#   remote   remote to push to (default: origin)

set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 <version> [remote]" >&2
  exit 2
fi

version=$1
remote=${2:-origin}

if [[ ! $version =~ ^v[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$ ]]; then
  echo "error: version must look like v1.2.3 or v1.2.3-rc.1, got '$version'" >&2
  exit 2
fi

git rev-parse --is-inside-work-tree >/dev/null

if [[ -n $(git status --porcelain) ]]; then
  echo "error: working tree is not clean" >&2
  exit 1
fi

if ! git remote get-url "$remote" >/dev/null 2>&1; then
  echo "error: remote '$remote' does not exist" >&2
  exit 1
fi

if git rev-parse -q --verify "refs/tags/$version" >/dev/null; then
  echo "error: tag '$version' already exists locally" >&2
  exit 1
fi

if git ls-remote --exit-code --tags "$remote" "refs/tags/$version" >/dev/null 2>&1; then
  echo "error: tag '$version' already exists on '$remote'" >&2
  exit 1
fi

# -s creates a signed, annotated tag. It needs user.signingkey (and gpg.format for SSH/X.509 keys).
git tag -s "$version" -m "Release $version"

# Don't push if the signature doesn't verify.
if ! git tag -v "$version" >/dev/null 2>&1; then
  echo "error: signature verification failed; removing local tag" >&2
  git tag -d "$version" >/dev/null
  exit 1
fi

# Push only this tag, not every local tag.
git push "$remote" "refs/tags/$version"

echo "Released $version to $remote"
```

The script runs these checks before it tags anything:
- **Version format:** it must look like `v1.2.3` or `v1.2.3-rc.1`.
- **Clean tree:** it refuses to run if the working tree has uncommitted changes.
- **Remote:** the remote must exist.
- **Existing tag:** the tag must not already exist locally or on the remote.

After tagging, it verifies the signature and deletes the local tag if verification fails. It then pushes only that one tag.

Two caveats:
- **Signing key:** you need a signing key configured, for example `git config user.signingkey <key>`. For SSH signing, also set `git config gpg.format ssh`.
- **Verification:** `git tag -v` needs the signer's public key to be trusted locally. For SSH signing, that means `gpg.ssh.allowedSignersFile` must be set.

I haven't run the script, so nothing has been tagged or pushed.
