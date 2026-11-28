I don't have a file-writing tool in this session, so the script is below. Save it as something like `scripts/release-tag.sh` and run `chmod +x` on it.

```bash
#!/usr/bin/env bash
# release-tag.sh: create a signed, annotated release tag and push it.
#
# Usage: release-tag.sh [-r remote] [-b branch] [-m message] [-n] <version>
#   <version>   Semantic version, with or without a leading "v" (e.g. 1.4.0 or v1.4.0-rc.1)
#   -r remote   Remote to push to (default: origin)
#   -b branch   Branch the release must be cut from (default: main)
#   -m message  Tag message (default: "Release <tag>")
#   -n          Dry run: run all checks and print the commands without running them

set -euo pipefail

remote="origin"
branch="main"
message=""
dry_run=0

die()  { printf 'error: %s\n' "$*" >&2; exit 1; }
info() { printf '==> %s\n' "$*"; }
run()  {
  if (( dry_run )); then printf '[dry-run] %q ' "$@"; printf '\n'; else "$@"; fi
}

usage() { sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'; exit "${1:-0}"; }

while getopts ":r:b:m:nh" opt; do
  case "$opt" in
    r) remote="$OPTARG" ;;
    b) branch="$OPTARG" ;;
    m) message="$OPTARG" ;;
    n) dry_run=1 ;;
    h) usage 0 ;;
    :) die "option -$OPTARG requires an argument" ;;
    *) die "unknown option -$OPTARG (see -h)" ;;
  esac
done
shift $((OPTIND - 1))
(( $# == 1 )) || usage 1

# --- Validate the version ---------------------------------------------------
version="${1#v}"
semver_re='^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-[0-9A-Za-z.-]+)?(\+[0-9A-Za-z.-]+)?$'
[[ "$version" =~ $semver_re ]] || die "'$1' is not a valid semantic version"
tag="v${version}"
message="${message:-Release ${tag}}"

# --- Check the repository state ---------------------------------------------
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "not inside a git repository"
git remote get-url "$remote" >/dev/null 2>&1 || die "remote '$remote' does not exist"

current_branch="$(git symbolic-ref --quiet --short HEAD || true)"
[[ "$current_branch" == "$branch" ]] \
  || die "on branch '${current_branch:-<detached>}', expected '$branch'"

[[ -z "$(git status --porcelain --untracked-files=no)" ]] \
  || die "working tree has uncommitted changes"

info "Fetching $remote"
git fetch --quiet --tags "$remote" "$branch"

local_sha="$(git rev-parse HEAD)"
remote_sha="$(git rev-parse "refs/remotes/${remote}/${branch}")"
[[ "$local_sha" == "$remote_sha" ]] \
  || die "HEAD ($local_sha) does not match ${remote}/${branch} ($remote_sha); push or pull first"

git rev-parse -q --verify "refs/tags/${tag}" >/dev/null \
  && die "tag '$tag' already exists locally"
git ls-remote --exit-code --tags "$remote" "refs/tags/${tag}" >/dev/null 2>&1 \
  && die "tag '$tag' already exists on '$remote'"

# --- Check the signing setup ------------------------------------------------
sign_format="$(git config --get gpg.format || echo openpgp)"
signing_key="$(git config --get user.signingkey || true)"
if [[ -z "$signing_key" && "$sign_format" != "openpgp" ]]; then
  die "user.signingkey is not set (required for gpg.format=$sign_format)"
fi
if [[ "$sign_format" == "ssh" && -z "$(git config --get gpg.ssh.allowedSignersFile || true)" ]]; then
  die "gpg.ssh.allowedSignersFile is not set; it is needed to verify the SSH-signed tag"
fi

# --- Tag, verify, push ------------------------------------------------------
info "Creating signed tag $tag at ${local_sha:0:12} (format: $sign_format)"
if [[ -n "$signing_key" ]]; then
  run git tag --sign --local-user="$signing_key" --message="$message" "$tag" "$local_sha"
else
  run git tag --sign --message="$message" "$tag" "$local_sha"
fi

if (( ! dry_run )); then
  info "Verifying signature"
  git tag --verify "$tag" || { git tag --delete "$tag" >/dev/null; die "signature verification failed; tag removed"; }
fi

info "Pushing $tag to $remote"
run git push --atomic "$remote" "refs/tags/${tag}"

info "Done: $tag"
```

**What it does:**
- **Checks before tagging:** The version must be valid semver. You must be on the release branch with no uncommitted changes. `HEAD` must match the remote branch, so the tag can't point at a commit that was never pushed. The tag must not already exist, either locally or on the remote.
- **Signing:** It uses `git tag --sign`, so it works with whatever you've set in `gpg.format` (OpenPGP, SSH or X.509). If you've set `user.signingkey`, it uses that key. For SSH signing it requires `gpg.ssh.allowedSignersFile`, because the verification step can't work without it.
- **Checks after tagging:** It runs `git tag --verify` before pushing. If verification fails, it deletes the local tag and stops, so an unverifiable tag never gets pushed.
- **Push:** It pushes only that one tag (`refs/tags/<tag>`). It doesn't use `--tags`, which would also push any stray local tags.

**Examples:**
```bash
./release-tag.sh -n 1.4.0                       # dry run: checks only, prints the commands
./release-tag.sh 1.4.0                          # tag v1.4.0 on main and push it to origin
./release-tag.sh -b release/1.x -m "LTS patch" v1.3.7
```

The `v` prefix and the `main` default are assumptions about your setup, so change them if your project does it differently.
