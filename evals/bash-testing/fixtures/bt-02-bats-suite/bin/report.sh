#!/usr/bin/env bash
# Summarize a CSV of build results.

set -euo pipefail

main() {
  local file="${1:-}"

  if [[ -z ${file} ]]; then
    printf 'usage: %s FILE\n' "${0##*/}" >&2
    return 64
  fi

  if [[ ! -r ${file} ]]; then
    printf '%s: cannot read %s\n' "${0##*/}" "${file}" >&2
    return 66
  fi

  local total=0 passed=0 failed=0
  local status

  while IFS=, read -r _ status _; do
    if [[ ${status} == 'status' ]]; then
      continue
    fi
    total=$((total + 1))
    case "${status}" in
      pass) passed=$((passed + 1)) ;;
      *) failed=$((failed + 1)) ;;
    esac
  done < "${file}"

  printf 'total=%d passed=%d failed=%d\n' "${total}" "${passed}" "${failed}"
}

main "$@"
