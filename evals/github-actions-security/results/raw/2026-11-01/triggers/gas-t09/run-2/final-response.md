I can't create files in this session, so here is the script for you to save as `release-tag.sh`:

```bash
#!/usr/bin/env bash
#
# release-tag.sh: create a signed, annotated release tag and push it.
#
# Usage: release-tag.sh [-r remote] [-b branch] [-m message] [-n] <version>
#   <version>   Release version, e.g. 1.4.0 or v1.4.0 (the "v" prefix is added if missing)
#   -r remote   Remote to push to (default: origin)
#   -b branch   Branch releases must be cut from (default: the remote's default branch)
#   -m message  Tag message (default: "Release <tag>")
#   -n          Dry run: run all the checks, but don't create or push the tag
#   -h          Show this help

set -Eeuo pipefail

die()  { printf 'error: %s\n' "$*" >&2; exit 1; }
info() { printf '==> %s\n' "$*"; }
usage() { sed -n '3,12p' "$0" | sed 's/^# \{0,1\}//'; }

remote="origin"
branch=""
message=""
dry_run=0

while getopts ':r:b:m:nh' opt; do
  case "$opt" in
    r) remote=$OPTARG ;;
    b) branch=$OPTARG ;;
    m) message=$OPTARG ;;
    n) dry_run=1 ;;
    h) usage; exit 0 ;;
    :) die "option -$OPTARG requires an argument" ;;
    *) die "unknown option -$OPTARG (see -h)" ;;
  esac
done
shift $((OPTIND - 1))

[[ $# -eq 1 ]] || { usage >&2; exit 2; }

version=${1#v}
tag="v${version}"

# Semantic version: MAJOR.MINOR.PATCH with an optional -prerelease and +build.
semver_re='^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-[0-9A-Za-z.-]+)?(\+[0-9A-Za-z.-]+)?$'
[[ $version =~ $semver_re ]] || die "'$1' is not a valid semantic version (expected e.g. 1.2.3)"
git check-ref-format "refs/tags/${tag}" || die "'$tag' is not a valid tag name"
: "${message:=Release ${tag}}"

# --- Preconditions -----------------------------------------------------------

command -v git >/dev/null || die "git is not installed"
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "not inside a git work tree"
cd "$(git rev-parse --show-toplevel)"

git remote get-url "$remote" >/dev/null 2>&1 || die "remote '$remote' does not exist"

# Signing must be configured: a key, or another format such as SSH or x509.
signing_key=$(git config --get user.signingkey || true)
gpg_format=$(git config --get gpg.format || echo openpgp)
if [[ -z $signing_key && $gpg_format == openpgp ]]; then
  command -v gpg >/dev/null || die "no user.signingkey set and gpg is not installed"
  gpg --list-secret-keys >/dev/null 2>&1 || die "no GPG secret keys available for signing"
fi

info "Fetching from '$remote'"
git fetch --quiet --tags --prune "$remote"

if [[ -z $branch ]]; then
  branch=$(git symbolic-ref --quiet --short "refs/remotes/${remote}/HEAD" 2>/dev/null || true)
  branch=${branch#"${remote}/"}
  [[ -n $branch ]] || die "can't determine the default branch of '$remote'; pass -b"
fi

current=$(git symbolic-ref --quiet --short HEAD || true)
[[ -n $current ]] || die "HEAD is detached; check out '$branch' first"
[[ $current == "$branch" ]] || die "on branch '$current', but releases are cut from '$branch'"

git diff --quiet && git diff --cached --quiet || die "working tree has uncommitted changes"
[[ -z $(git ls-files --others --exclude-standard) ]] || die "working tree has untracked files"

local_sha=$(git rev-parse HEAD)
remote_sha=$(git rev-parse --verify --quiet "refs/remotes/${remote}/${branch}" || true)
[[ -n $remote_sha ]] || die "branch '$branch' does not exist on '$remote'"
[[ $local_sha == "$remote_sha" ]] \
  || die "local '$branch' ($local_sha) is not in sync with ${remote}/${branch} ($remote_sha); pull or push first"

if git rev-parse --verify --quiet "refs/tags/${tag}" >/dev/null; then
  die "tag '$tag' already exists locally"
fi
if git ls-remote --exit-code --tags "$remote" "refs/tags/${tag}" >/dev/null 2>&1; then
  die "tag '$tag' already exists on '$remote'"
fi

# --- Tag, verify, push -------------------------------------------------------

info "Release:  $tag"
info "Commit:   $local_sha ($(git log -1 --format=%s HEAD))"
info "Remote:   $remote ($(git remote get-url "$remote"))"

if (( dry_run )); then
  info "Dry run: all checks passed. Nothing was tagged or pushed."
  exit 0
fi

# If anything below fails, delete the local tag so the script can be re-run cleanly.
tag_created=0
cleanup() {
  local rc=$?
  if (( rc != 0 && tag_created )); then
    printf 'warning: removing local tag %s after failure\n' "$tag" >&2
    git tag -d "$tag" >/dev/null 2>&1 || true
  fi
  exit "$rc"
}
trap cleanup EXIT

info "Creating signed tag $tag"
git tag --sign --message "$message" -- "$tag" "$local_sha"
tag_created=1

info "Verifying signature"
git tag --verify -- "$tag" || die "signature verification failed for '$tag'"

info "Pushing $tag to $remote"
# Push only this tag, not every local tag. A tag that already exists on the remote is never overwritten.
git push --no-follow-tags "$remote" "refs/tags/${tag}:refs/tags/${tag}"
tag_created=0   # pushed, so keep the local tag even if a later step fails

info "Done: $tag pushed to $remote"
```

To use it:

```bash
chmod +x release-tag.sh
./release-tag.sh -n 1.4.0         # dry run: checks only
./release-tag.sh 1.4.0            # creates and pushes v1.4.0 to origin
./release-tag.sh -r upstream -b main -m "Release 1.4.0: new parser" v1.4.0
```

**What it checks before tagging:**
- **Version format:** the version must be valid semver, and a `v` prefix is added if you leave it off.
- **Signing setup:** you need a signing key or a non-GPG signing format. SSH signing works if you set `git config gpg.format ssh` and point `user.signingkey` at your SSH key.
- **Branch and working tree:** you must be on the release branch (by default, the remote's default branch), with no uncommitted or untracked files, and your branch must match the remote's copy exactly. That way the tag lands on a commit that's already pushed.
- **No duplicate tag:** the tag must not already exist, locally or on the remote.

**Other notes:**
- After creating the tag, the script checks the signature with `git tag --verify` before pushing.
- It pushes only this one tag, so other local tags stay where they are and an existing remote tag is never overwritten.
- If signing, verifying or pushing fails, it deletes the local tag so you can fix the problem and run it again.

I haven't run it here. Try `-n` first to confirm the checks pass in your repository.
