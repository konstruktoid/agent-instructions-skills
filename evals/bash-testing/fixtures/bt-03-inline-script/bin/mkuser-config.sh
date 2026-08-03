#!/usr/bin/env bash
# Append one provisioning entry to the users configuration.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly ROOT

# shellcheck source=lib/format.sh
source "${ROOT}/lib/format.sh"

name=''
login_shell='/bin/bash'
out="${ROOT}/config/users.conf"

while (($# > 0)); do
  case "$1" in
    --name)
      name="${2:-}"
      shift 2
      ;;
    --shell)
      login_shell="${2:-}"
      shift 2
      ;;
    --out)
      out="${2:-}"
      shift 2
      ;;
    *)
      printf 'unknown option: %s\n' "$1" >&2
      exit 64
      ;;
  esac
done

mkdir -p -- "$(dirname -- "${out}")"
format_line "${name}" "${login_shell}" >> "${out}"
printf 'wrote %s for %s\n' "${out}" "${name}"
