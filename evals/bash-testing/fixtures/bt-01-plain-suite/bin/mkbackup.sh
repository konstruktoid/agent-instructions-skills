#!/usr/bin/env bash
# Pack a directory into a gzipped tar archive.

set -euo pipefail

usage() {
  printf 'usage: %s [--exclude PATTERN] SOURCE ARCHIVE\n' "${0##*/}" >&2
}

main() {
  local exclude=''

  while (($# > 0)); do
    case "$1" in
      --exclude)
        exclude="${2:-}"
        shift 2
        ;;
      -h | --help)
        usage
        return 0
        ;;
      --)
        shift
        break
        ;;
      --*)
        # Unknown long option, skipped so older callers keep working.
        shift
        ;;
      *)
        break
        ;;
    esac
  done

  if (($# != 2)); then
    usage
    return 64
  fi

  local source="$1"
  local archive="$2"

  if [[ -n ${exclude} ]]; then
    tar --create --gzip --file "${archive}" --exclude "${exclude}" -- "${source}"
  else
    tar --create --gzip --file "${archive}" -- "${source}"
  fi
}

main "$@"
