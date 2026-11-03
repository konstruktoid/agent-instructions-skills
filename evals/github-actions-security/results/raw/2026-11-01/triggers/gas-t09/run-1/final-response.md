I can't create files in this session, so here's the script to save as `release-tag.sh`:

```bash
#!/usr/bin/env bash
#
# release-tag.sh - create a signed, annotated release tag and push it.
#
# Usage: release-tag.sh [-r remote] [-b branch] [-m message] [-n] <version>
#   <version>   Semantic version, e.g. 1.4.0 or v1.4.0 (the tag gets a "v" prefix)
#   -r remote   Remote to push to (default: origin)
#   -b branch   Branch releases must be cut from (default: main)
#   -m message  Tag message (default: "Release v<version>")
#   -n          Dry run: run every check, but don't create or push the tag
#
# Signing uses whatever git is set up with (gpg.format = openpgp, ssh or x509,
# plus user.signingkey).

set -Eeuo pipefail

die() { printf 'error: %s\n' "$*" >&2; exit 1; }
log() { printf '==> %s\n' "$*" >&2; }

usage() {
  sed -n '3,13s/^# \{0,1\}//p' "$0" >&2
  exit "${1:-2}"
}

remote="origin"
branch="main"
message=""
dry_run=false

while getopts ':r:b:m:nh' opt; do
  case "$opt" in
    r) remote="$OPTARG" ;;
    b) branch="$OPTARG" ;;
    m) message="$OPTARG" ;;
    n) dry_run=true ;;
    h) usage 0 ;;
    :) die "option -$OPTARG requires an argument" ;;
    *) die "unknown option -$OPTARG" ;;
  esac
done
shift $((OPTIND - 1))

[[ $# -eq 1 ]] || usage
version="${1#v}"

# Strict SemVer 2.0.0 (optional pre-release and build metadata).
semver_re='^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-[0-9A-Za-z.-]+)?(\+[0-9A-Za-z.-]+)?$'
[[ "$version" =~ $semver_re ]] || die "'$1' is not a valid semantic version"

tag="v${version}"
message="${message:-Release ${tag}}"

# --- Pre-flight checks ------------------------------------------------------

command -v git >/dev/null 2>&1 || die "git not found"
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "not inside a git repository"
cd "$(git rev-parse --show-toplevel)"

git check-ref-format "refs/tags/${tag}" || die "'${tag}' is not a valid tag name"
git remote get-url "$remote" >/dev/null 2>&1 || die "remote '${remote}' does not exist"

current_branch="$(git symbolic-ref --quiet --short HEAD)" \
  || die "HEAD is detached; check out '${branch}' first"
[[ "$current_branch" == "$branch" ]] \
  || die "on branch '${current_branch}', expected '${branch}'"

if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
  die "working tree has uncommitted changes"
fi

log "Fetching ${remote}"
git fetch --quiet --tags "$remote" "$branch"

local_sha="$(git rev-parse HEAD)"
remote_sha="$(git rev-parse "refs/remotes/${remote}/${branch}")"
[[ "$local_sha" == "$remote_sha" ]] \
  || die "local '${branch}' (${local_sha:0:12}) differs from ${remote}/${branch} (${remote_sha:0:12}); pull or push first"

if git rev-parse --quiet --verify "refs/tags/${tag}" >/dev/null; then
  die "tag '${tag}' already exists locally"
fi
if git ls-remote --exit-code --tags "$remote" "refs/tags/${tag}" >/dev/null 2>&1; then
  die "tag '${tag}' already exists on '${remote}'"
fi

signing_key="$(git config --get user.signingkey || true)"
gpg_format="$(git config --get gpg.format || echo openpgp)"
if [[ -z "$signing_key" && "$gpg_format" == "ssh" ]]; then
  die "gpg.format is ssh but user.signingkey is not set"
fi

log "Tag:     ${tag}"
log "Commit:  ${local_sha}"
log "Remote:  ${remote}"
log "Signing: ${gpg_format}${signing_key:+ (${signing_key})}"

if $dry_run; then
  log "Dry run: all checks passed, nothing created or pushed"
  exit 0
fi

# --- Create, verify, push ---------------------------------------------------

cleanup_tag() {
  log "Removing local tag ${tag} after failure"
  git tag -d "$tag" >/dev/null 2>&1 || true
}

log "Creating signed tag ${tag}"
git tag --sign --message "$message" "$tag" "$local_sha" \
  || die "could not create signed tag (check your signing setup)"

trap cleanup_tag ERR

log "Verifying signature"
git tag --verify "$tag" >/dev/null 2>&1 \
  || { cleanup_tag; trap - ERR; die "signature on ${tag} could not be verified"; }

log "Pushing ${tag} to ${remote}"
# Push only this tag ref, never --tags, so stray local tags don't get published.
git push --atomic "$remote" "refs/tags/${tag}:refs/tags/${tag}"

trap - ERR
log "Released ${tag}"
```

Then make it executable and run it:

```bash
chmod +x release-tag.sh
./release-tag.sh -n 1.4.0     # dry run: checks only
./release-tag.sh 1.4.0        # creates signed tag v1.4.0 and pushes it to origin
./release-tag.sh -r upstream -b release/1.x -m "1.4.1 hotfix" 1.4.1
```

**Checks it runs before tagging:**
- The version must be valid SemVer. It's normalized to a `v`-prefixed tag, so `1.4.0` and `v1.4.0` both give `v1.4.0`.
- You must be on the expected branch, not a detached HEAD.
- Tracked files must have no uncommitted changes.
- Your local branch must match the remote after a fetch, so you can't tag a commit nobody else has.
- The tag must not already exist, locally or on the remote.

**Notes:**
- **Signing:** `git tag --sign` uses your existing git signing setup (GPG, SSH or X.509). The script checks the signature with `git tag --verify` before pushing. That step needs a verifier: for SSH signing, set `gpg.ssh.allowedSignersFile`.
- **Push:** It pushes only that one tag ref, never `--tags`, so leftover local tags don't get published.
- **On failure:** If verification or the push fails, the script deletes the local tag so you can fix the problem and run it again.

I haven't run this script. Try it with `-n` first to make sure the checks pass in your repo.
