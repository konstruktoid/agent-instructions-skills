#!/usr/bin/env bash
# Run every test/test_*.sh and summarize the result.

set -uo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 1

failed=0
for test_file in test/test_*.sh; do
  if bash "${test_file}"; then
    continue
  fi
  printf 'FAILED %s\n' "${test_file}" >&2
  failed=$((failed + 1))
done

if ((failed > 0)); then
  printf '%d test file(s) failed\n' "${failed}" >&2
  exit 1
fi

printf 'all test files passed\n'
