#!/usr/bin/env bash
# Remove build artifacts older than the retention window.

set -uo pipefail

readonly DEFAULT_DAYS=14

main() {
  local dir="${1:-artifacts}"
  local days="${2:-${DEFAULT_DAYS}}"

  if [[ -d ${dir} ]]; then
    find "${dir}" -type f -name '*.tar.gz' -mtime "+${days}" -delete
  fi

  printf 'pruned %s (older than %s days)\n' "${dir}" "${days}"
}

main "$@"
