I don't have a file-writing tool in this session, so the full script is below. Save it as `release-tag.sh` and run `chmod +x release-tag.sh`.

```bash
#!/usr/bin/env bash
#
# release-tag.sh: create a signed, annotated release tag and push it to a remote.
#
# Usage:
#   ./release-tag.sh [options] <version>
#
# Examples:
#   ./release-tag.sh 1.4.0
#   ./release-tag.sh -m "Release 1.4.0: new parser" -r upstream v1.4.0
#   ./release-tag.sh --dry-run 2.0.0-rc.1
#
# Signing uses your git config: GPG by default, or SSH/X.509 if gpg.format is
# set. Set user.signingkey for a specific key.

set -Eeuo pipefail

# ---------- defaults ----------
REMOTE="origin"
BRANCH=""            # empty = allow any branch; set with -b to enforce one
MESSAGE=""
PREFIX="v"
DRY_RUN=0
ASSUME_YES=0
ALLOW_DIRTY=0

# ---------- helpers ----------
die()  { printf 'error: %s\n' "$*" >&2; exit 1; }
info() { printf '==> %s\n' "$*"; }
run()  {
  if (( DRY_RUN )); then
    printf '[dry-run]'; printf ' %q' "$@"; printf '\n'
  else
    "$@"
  fi
}

usage() {
  cat <<EOF
Usage: ${0##*/} [options] <version>

Create a signed annotated tag for <version> on HEAD and push it.

Options:
  -r, --remote NAME     Remote to push to (default: origin)
  -b, --branch NAME     Require HEAD to be on this branch and in sync with remote
  -m, --message MSG     Tag message (default: "Release <tag>")
  -p, --prefix STR      Tag prefix added if missing (default: "v"; use "" for none)
  -n, --dry-run         Show what would happen without changing anything
  -y, --yes             Don't prompt for confirmation before pushing
      --allow-dirty     Skip the clean-working-tree check
  -h, --help            Show this help
EOF
}

# ---------- argument parsing ----------
VERSION=""
while (( $# )); do
  case "$1" in
    -r|--remote)   [[ $# -ge 2 ]] || die "$1 needs a value"; REMOTE="$2"; shift 2 ;;
    -b|--branch)   [[ $# -ge 2 ]] || die "$1 needs a value"; BRANCH="$2"; shift 2 ;;
    -m|--message)  [[ $# -ge 2 ]] || die "$1 needs a value"; MESSAGE="$2"; shift 2 ;;
    -p|--prefix)   [[ $# -ge 2 ]] || die "$1 needs a value"; PREFIX="$2"; shift 2 ;;
    -n|--dry-run)  DRY_RUN=1; shift ;;
    -y|--yes)      ASSUME_YES=1; shift ;;
    --allow-dirty) ALLOW_DIRTY=1; shift ;;
    -h|--help)     usage; exit 0 ;;
    --)            shift; break ;;
    -*)            die "unknown option: $1 (see --help)" ;;
    *)             [[ -z "$VERSION" ]] || die "only one version may be given"
                   VERSION="$1"; shift ;;
  esac
done
if [[ -z "$VERSION" && $# -gt 0 ]]; then VERSION="$1"; shift; fi
[[ $# -eq 0 ]] || die "unexpected arguments: $*"
[[ -n "$VERSION" ]] || { usage >&2; exit 2; }

# Normalise the tag name: "1.2.3" -> "v1.2.3" (unless it already has the prefix).
if [[ -n "$PREFIX" && "$VERSION" != "$PREFIX"* ]]; then
  TAG="${PREFIX}${VERSION}"
else
  TAG="$VERSION"
fi

# Basic SemVer check on the part after the prefix.
SEMVER_RE='^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-[0-9A-Za-z.-]+)?(\+[0-9A-Za-z.-]+)?$'
[[ "${TAG#"$PREFIX"}" =~ $SEMVER_RE ]] \
  || die "'$TAG' is not a valid semantic version (expected e.g. ${PREFIX}1.2.3)"
git check-ref-format "refs/tags/$TAG" || die "'$TAG' is not a valid git tag name"

MESSAGE="${MESSAGE:-Release $TAG}"

# ---------- pre-flight checks ----------
command -v git >/dev/null || die "git is not installed"
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "not inside a git repository"
cd "$(git rev-parse --show-toplevel)"

git remote get-url "$REMOTE" >/dev/null 2>&1 || die "remote '$REMOTE' does not exist"

# Signing must be configured, otherwise `git tag -s` fails partway through.
SIGN_FORMAT="$(git config --get gpg.format || echo openpgp)"
SIGN_KEY="$(git config --get user.signingkey || true)"
case "$SIGN_FORMAT" in
  openpgp)
    command -v "$(git config --get gpg.program || echo gpg)" >/dev/null \
      || die "gpg not found; install GnuPG or set gpg.program"
    if [[ -z "$SIGN_KEY" ]]; then
      info "user.signingkey not set; gpg will pick a key from your committer email"
    fi
    ;;
  ssh)
    [[ -n "$SIGN_KEY" ]] || die "gpg.format=ssh requires user.signingkey to be set"
    ;;
  x509) ;;
  *) die "unsupported gpg.format '$SIGN_FORMAT'" ;;
esac

if (( ! ALLOW_DIRTY )); then
  git update-index -q --refresh
  git diff-index --quiet HEAD -- \
    || die "working tree has uncommitted changes (commit/stash them, or use --allow-dirty)"
  [[ -z "$(git ls-files --others --exclude-standard)" ]] \
    || die "working tree has untracked files (clean them up, or use --allow-dirty)"
fi

info "Fetching tags from '$REMOTE'..."
git fetch --quiet --tags "$REMOTE"

git rev-parse -q --verify "refs/tags/$TAG" >/dev/null \
  && die "tag '$TAG' already exists locally"
git ls-remote --exit-code --tags "$REMOTE" "refs/tags/$TAG" >/dev/null 2>&1 \
  && die "tag '$TAG' already exists on '$REMOTE'"

if [[ -n "$BRANCH" ]]; then
  CURRENT="$(git symbolic-ref --quiet --short HEAD || echo '(detached)')"
  [[ "$CURRENT" == "$BRANCH" ]] || die "on branch '$CURRENT', expected '$BRANCH'"
  git fetch --quiet "$REMOTE" "$BRANCH"
  LOCAL_SHA="$(git rev-parse HEAD)"
  REMOTE_SHA="$(git rev-parse FETCH_HEAD)"
  [[ "$LOCAL_SHA" == "$REMOTE_SHA" ]] \
    || die "'$BRANCH' is not in sync with '$REMOTE/$BRANCH' (pull or push first)"
fi

COMMIT="$(git rev-parse HEAD)"

# ---------- summary & confirmation ----------
cat <<EOF

  Tag:      $TAG
  Commit:   $COMMIT  ($(git log -1 --format=%s HEAD))
  Remote:   $REMOTE ($(git remote get-url "$REMOTE"))
  Signing:  $SIGN_FORMAT${SIGN_KEY:+ (key: $SIGN_KEY)}
  Message:  $MESSAGE

EOF

if (( ! ASSUME_YES && ! DRY_RUN )); then
  read -r -p "Create and push this signed tag? [y/N] " reply
  [[ "$reply" =~ ^[Yy]([Ee][Ss])?$ ]] || die "aborted by user"
fi

# ---------- create, verify, push ----------
CREATED=0
cleanup() {
  # If anything fails after the tag was created but before the push succeeded,
  # remove the local tag so a re-run starts clean.
  if (( CREATED )); then
    printf 'warning: push failed, deleting local tag %s\n' "$TAG" >&2
    git tag -d "$TAG" >/dev/null 2>&1 || true
  fi
}
trap cleanup ERR

info "Creating signed tag $TAG..."
run git tag --sign --message "$MESSAGE" "$TAG" "$COMMIT"
(( DRY_RUN )) || CREATED=1

info "Verifying signature..."
run git tag --verify "$TAG"

info "Pushing $TAG to $REMOTE..."
# Push only this tag. --tags would publish every local tag.
run git push "$REMOTE" "refs/tags/$TAG"
CREATED=0
trap - ERR

info "Done: $TAG pushed to $REMOTE."
```

**What it does:**
- **Checks before tagging:** it confirms you're in a git repo, the remote exists, signing is set up (GPG, SSH or X.509 via `gpg.format`), the working tree is clean, and the tag doesn't already exist locally or on the remote. With `-b main`, it also checks that you're on that branch and that it matches the remote.
- **Signs and verifies:** it creates an annotated tag with `git tag --sign`, then runs `git tag --verify` before pushing, so an unsigned or broken tag never gets published.
- **Pushes only the new tag:** it uses `git push <remote> refs/tags/<tag>` instead of `--tags`, so other local tags you have lying around aren't pushed by accident.
- **Cleans up on failure:** if verifying or pushing fails, it deletes the local tag so you can run the script again.
- **Normalises and validates the version:** `1.2.3` becomes `v1.2.3` (change this with `-p ""`), and anything that isn't a valid semantic version is rejected.
- **Asks before pushing:** it shows a summary and asks for confirmation. Use `--yes` for CI and `--dry-run` to preview the steps.

**One-time signing setup** if you haven't done it yet:
```bash
# GPG
git config --global user.signingkey <KEY_ID>

# or SSH
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub
```

For `git tag --verify` to work with SSH signing, you also need `gpg.ssh.allowedSignersFile` set up.
