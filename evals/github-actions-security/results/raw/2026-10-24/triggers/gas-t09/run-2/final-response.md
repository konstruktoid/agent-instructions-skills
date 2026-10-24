I don't have a file-writing tool in this session, so the script is below for you to save, for example as `scripts/release-tag.sh`.

```bash
#!/usr/bin/env bash
#
# release-tag.sh - create a signed, annotated release tag and push it.
#
# Usage: release-tag.sh [-r remote] [-b branch] [-m message] [-n] <version>
#   <version>   Semantic version, with or without a leading "v" (e.g. 1.4.0 or v1.4.0)
#   -r remote   Remote to push to (default: origin)
#   -b branch   Branch releases must be cut from (default: main)
#   -m message  Tag message (default: "Release <tag>")
#   -n          Dry run: run all checks and print what would happen, but make no changes
#
# Signing uses your git config (user.signingkey, gpg.format = openpgp|ssh|x509).

set -euo pipefail

remote="origin"
branch="main"
message=""
dry_run=0

die()  { printf 'error: %s\n' "$*" >&2; exit 1; }
info() { printf '==> %s\n' "$*"; }
run()  {
  if (( dry_run )); then
    printf '[dry-run] %s\n' "$*"
  else
    "$@"
  fi
}

usage() { sed -n '3,12p' "$0" | sed 's/^# \{0,1\}//'; exit "${1:-0}"; }

while getopts ':r:b:m:nh' opt; do
  case "$opt" in
    r) remote="$OPTARG" ;;
    b) branch="$OPTARG" ;;
    m) message="$OPTARG" ;;
    n) dry_run=1 ;;
    h) usage 0 ;;
    :) die "option -$OPTARG requires an argument" ;;
    *) usage 1 ;;
  esac
done
shift $((OPTIND - 1))

(( $# == 1 )) || usage 1

version="${1#v}"
tag="v${version}"
semver_re='^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-[0-9A-Za-z.-]+)?(\+[0-9A-Za-z.-]+)?$'
[[ "$version" =~ $semver_re ]] || die "'$1' is not a valid semantic version"
: "${message:=Release ${tag}}"

# --- Preconditions ----------------------------------------------------------

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "not inside a git repository"
git remote get-url "$remote" >/dev/null 2>&1 || die "remote '$remote' does not exist"

current_branch="$(git symbolic-ref --quiet --short HEAD)" || die "HEAD is detached"
[[ "$current_branch" == "$branch" ]] \
  || die "on branch '$current_branch', releases must be tagged from '$branch'"

git diff --quiet && git diff --cached --quiet \
  || die "working tree has uncommitted changes"
[[ -z "$(git ls-files --others --exclude-standard)" ]] \
  || die "working tree has untracked files"

info "Fetching from $remote"
git fetch --quiet "$remote" "$branch"

local_sha="$(git rev-parse HEAD)"
remote_sha="$(git rev-parse "refs/remotes/${remote}/${branch}")"
[[ "$local_sha" == "$remote_sha" ]] \
  || die "local '$branch' ($local_sha) differs from '$remote/$branch' ($remote_sha); push or pull first"

git rev-parse -q --verify "refs/tags/${tag}" >/dev/null \
  && die "tag '$tag' already exists locally"
[[ -z "$(git ls-remote --tags "$remote" "refs/tags/${tag}")" ]] \
  || die "tag '$tag' already exists on '$remote'"

# Make sure signing is configured before tagging, so it doesn't fail halfway.
fmt="$(git config --get gpg.format || echo openpgp)"
if [[ "$fmt" == "ssh" ]]; then
  git config --get user.signingkey >/dev/null \
    || die "gpg.format=ssh but user.signingkey is not set"
elif [[ "$fmt" == "openpgp" ]]; then
  command -v "$(git config --get gpg.program || echo gpg)" >/dev/null \
    || die "gpg not found; install it or set gpg.program"
fi

# --- Tag, verify, push --------------------------------------------------------

info "Creating signed tag $tag at ${local_sha:0:12} ($fmt)"
run git tag --sign --annotate "$tag" --message "$message" "$local_sha"

if (( ! dry_run )); then
  info "Verifying signature"
  git tag --verify "$tag" >/dev/null 2>&1 || {
    git tag --delete "$tag" >/dev/null
    die "signature verification failed; local tag removed"
  }
fi

info "Pushing $tag to $remote"
if ! run git push --atomic "$remote" "refs/tags/${tag}"; then
  git tag --delete "$tag" >/dev/null
  die "push failed; local tag removed"
fi

info "Done: $tag -> $(git remote get-url "$remote")"
```

Usage:

```bash
chmod +x scripts/release-tag.sh
scripts/release-tag.sh -n 1.4.0     # dry run: checks only, no changes
scripts/release-tag.sh 1.4.0        # creates and pushes signed tag v1.4.0
scripts/release-tag.sh -r upstream -b release/1.x -m "1.4.1 hotfix" v1.4.1
```

**What it checks before tagging:**
- The version is valid semver. A leading `v` is optional; the tag is always `v<version>`.
- You're on the release branch with no uncommitted or untracked files.
- Your local branch matches the remote one, so the tag never points to a commit that isn't on the remote.
- The tag doesn't already exist, either locally or on the remote.
- Signing is set up. It works with GPG, SSH (`gpg.format=ssh`) or x509, using your existing git config.

**Safety choices:**
- It pushes only the new tag (`refs/tags/vX.Y.Z`), never `--tags`, so stray local tags don't get published.
- It checks the signature with `git tag --verify` before pushing. If that check or the push fails, it deletes the local tag so you can simply run it again.
- `-n` runs every check and shows what it would do, without changing anything.

I haven't run the script here. Try it with `-n` first.
