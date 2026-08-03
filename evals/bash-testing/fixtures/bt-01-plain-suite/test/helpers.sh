# Assertions shared by the test/test_*.sh scripts.
# shellcheck shell=bash

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export REPO_ROOT

fail() {
  printf 'FAIL %s: %s\n' "${TEST_NAME:-test}" "$*" >&2
  exit 1
}

assert_status() {
  local expected="$1"
  local actual="$2"
  ((expected == actual)) || fail "expected status ${expected}, got ${actual}"
}

assert_contains() {
  local haystack="$1"
  local needle="$2"
  [[ ${haystack} == *"${needle}"* ]] || fail "expected ${needle} in ${haystack}"
}

make_tree() {
  local dir="$1"
  mkdir -p -- "${dir}/keepme" "${dir}/skipme"
  printf 'keep\n' > "${dir}/keepme/file.txt"
  printf 'skip\n' > "${dir}/skipme/file.txt"
}
