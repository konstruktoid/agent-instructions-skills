#!/usr/bin/env bash
# Coverage for the archive creation path of bin/mkbackup.sh.

set -uo pipefail

TEST_NAME='mkbackup basic'
# shellcheck source=test/helpers.sh
source "$(dirname "${BASH_SOURCE[0]}")/helpers.sh"

workdir="$(mktemp -d)"
trap 'rm -rf -- "${workdir}"' EXIT

make_tree "${workdir}/src"

"${REPO_ROOT}/bin/mkbackup.sh" "${workdir}/src" "${workdir}/out.tar.gz"
assert_status 0 $?
[[ -s ${workdir}/out.tar.gz ]] || fail 'archive was not created'

contents="$(tar --list --file "${workdir}/out.tar.gz")"
assert_contains "${contents}" 'keepme/file.txt'

"${REPO_ROOT}/bin/mkbackup.sh" "${workdir}/src" > /dev/null 2>&1
assert_status 64 $?

"${REPO_ROOT}/bin/mkbackup.sh" --exclude 'skipme' "${workdir}/src" "${workdir}/excluded.tar.gz"
contents="$(tar --list --file "${workdir}/excluded.tar.gz")"
[[ ${contents} == *skipme* ]] && fail 'excluded directory is present in the archive'

printf 'PASS %s\n' "${TEST_NAME}"
