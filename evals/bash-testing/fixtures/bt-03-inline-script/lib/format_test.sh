#!/usr/bin/env bash
# Coverage for lib/format.sh.

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly ROOT

# shellcheck source=lib/format.sh
source "${ROOT}/lib/format.sh"

result="$(format_line alice /bin/bash)"
if [[ ${result} != 'alice:/bin/bash' ]]; then
  printf 'format_line returned %s\n' "${result}" >&2
  exit 1
fi

printf 'ok lib/format.sh\n'
