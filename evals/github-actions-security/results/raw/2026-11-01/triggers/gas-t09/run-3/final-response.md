I couldn't save this to a file because I don't have a write tool in this session. Save it as `release.sh` and run `chmod +x release.sh`.

```bash
#!/usr/bin/env bash
#
# release.sh — create a signed, annotated release tag and push it to a remote.
#
# Usage:
#   release.sh [-r remote] [-b branch] [-m message] [-n] <version>
#
#   <version>   Release version, e.g. 1.4.0 or v1.4.0 (a leading "v" is added if missing)
#   -r remote   Remote to push to (default: origin)
#   -b branch   Branch the release must be cut from (default: main)
#   -m message  Tag message (default: "Release <tag>")
#   -n          Dry run: run every check, but don't create or push the tag
#
# Signing uses your git configuration (user.signingkey, gpg.format = openpgp|ssh|x509).

set -euo pipefail

readonly PROG="${0##*/}"

die()  { printf '%s: error: %s\n' "$PROG" "$*" >&2; exit 1; }
info() { printf '%s: %s\n' "$PROG" "$*" >&2; }

usage() {
  sed -n '3,15p' "$0" | sed 's/^# \{0,1\}//'
  exit "${1:-0}"
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
    *) die "unknown option -$OPTARG (see -h)" ;;
  esac
done
shift $((OPTIND - 1))

[[ $# -eq 1 ]] || usage 2

version="$1"
tag="v${version#v}"
message="${message:-Release $tag}"

# --- Validate the version string (SemVer 2.0.0, optional pre-release/build) ---
semver_re='^v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-[0-9A-Za-z.-]+)?(\+[0-9A-Za-z.-]+)?$'
[[ "$tag" =~ $semver_re ]] || die "'$tag' is not a valid semantic version (expected vMAJOR.MINOR.PATCH)"

# --- Repository sanity checks ---
command -v git >/dev/null 2>&1 || die "git is not installed"
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "not inside a git work tree"

git remote get-url "$remote" >/dev/null 2>&1 || die "remote '$remote' does not exist"

current_branch="$(git symbolic-ref --quiet --short HEAD || true)"
[[ -n "$current_branch" ]] || die "HEAD is detached; check out '$branch' first"
[[ "$current_branch" == "$branch" ]] || die "on branch '$current_branch', expected '$branch' (use -b to override)"

# Refuse to tag with uncommitted or untracked changes
if [[ -n "$(git status --porcelain)" ]]; then
  die "working tree is not clean; commit or stash your changes first"
fi

# --- Make sure local branch matches the remote ---
info "fetching from '$remote'..."
git fetch --quiet --tags "$remote" "$branch"

local_sha="$(git rev-parse HEAD)"
remote_sha="$(git rev-parse "refs/remotes/$remote/$branch" 2>/dev/null || true)"
[[ -n "$remote_sha" ]] || die "branch '$branch' not found on '$remote'"
[[ "$local_sha" == "$remote_sha" ]] || die "local '$branch' ($local_sha) differs from $remote/$branch ($remote_sha); pull/push first"

# --- Tag must not already exist, locally or remotely ---
if git rev-parse -q --verify "refs/tags/$tag" >/dev/null; then
  die "tag '$tag' already exists locally"
fi
if git ls-remote --exit-code --tags "$remote" "refs/tags/$tag" >/dev/null 2>&1; then
  die "tag '$tag' already exists on '$remote'"
fi

# --- Signing configuration ---
sign_format="$(git config --get gpg.format || echo openpgp)"
signing_key="$(git config --get user.signingkey || true)"
if [[ "$sign_format" == "ssh" && -z "$signing_key" ]]; then
  die "gpg.format is ssh but user.signingkey is not set"
fi
if [[ "$sign_format" == "openpgp" ]]; then
  command -v "$(git config --get gpg.program || echo gpg)" >/dev/null 2>&1 \
    || die "gpg program not found; install GnuPG or set gpg.program"
fi

info "release:  $tag"
info "commit:   $local_sha ($branch)"
info "remote:   $remote ($(git remote get-url "$remote"))"
info "signing:  $sign_format${signing_key:+ (key: $signing_key)}"

if $dry_run; then
  info "dry run: all checks passed; no tag created or pushed"
  exit 0
fi

# --- Create the signed, annotated tag ---
cleanup_tag() {
  # If something fails after the tag exists locally but before it's pushed, delete it
  # so the next run starts clean.
  if [[ "${pushed:-false}" != true ]] && git rev-parse -q --verify "refs/tags/$tag" >/dev/null; then
    info "removing local tag '$tag' after failure"
    git tag -d "$tag" >/dev/null || true
  fi
}
trap cleanup_tag ERR INT TERM

pushed=false
if [[ -n "$signing_key" ]]; then
  git tag --local-user="$signing_key" --sign --message="$message" "$tag" "$local_sha"
else
  git tag --sign --message="$message" "$tag" "$local_sha"
fi

# Verify the signature before publishing
git tag --verify "$tag" >/dev/null 2>&1 || die "signature verification failed for '$tag'"
info "created and verified signed tag '$tag'"

# --- Push only this tag (not --tags, which would publish every local tag) ---
git push --atomic "$remote" "refs/tags/$tag"
pushed=true
trap - ERR INT TERM

info "pushed '$tag' to '$remote'"
```

**Example usage:**
```bash
./release.sh -n 1.4.0          # dry run: checks only, creates nothing
./release.sh 1.4.0             # tags v1.4.0 on main and pushes it to origin
./release.sh -r upstream -b release/1.x -m "1.4.1 hotfix" v1.4.1
```

**What it does:**
- **Checks the version:** it accepts `1.2.3` or `v1.2.3` and always creates a tag with a `v` prefix.
- **Checks the repo before tagging:** you must be on the expected branch with no uncommitted or untracked changes, and your branch must match the remote. That way the tag points at a commit everyone else can fetch.
- **Won't overwrite a tag:** it stops if the tag already exists locally or on the remote. It never force-pushes.
- **Works with any signing method:** it uses your git signing setup (GPG, SSH or X.509). If `user.signingkey` is set, it uses that key.
- **Checks the signature before pushing:** an unsigned or broken tag never leaves your machine.
- **Pushes only the new tag:** it uses `refs/tags/<tag>` instead of `--tags`, so other local tags (for example, old experiments) aren't published by accident.
- **Cleans up after a failure:** if the signature check or the push fails, it deletes the local tag so you can run the script again.

**One-time setup if you haven't configured signing:**
```bash
# SSH signing
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub

# or GPG
git config --global user.signingkey <KEY_ID>
```

To make GitHub or GitLab show the tag as "Verified," also upload the same key there as a **signing key**.
