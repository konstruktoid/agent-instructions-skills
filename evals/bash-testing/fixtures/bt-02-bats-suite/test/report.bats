#!/usr/bin/env bats

load test_helper

@test "summarizes a mixed result file" {
  run "${REPO_ROOT}/bin/report.sh" "${REPO_ROOT}/data/sample.csv"
  [ "$status" -eq 0 ]
  [ "$output" = "total=3 passed=2 failed=1" ]
}

@test "reports usage when no file is given" {
  run "${REPO_ROOT}/bin/report.sh"
  [ "$status" -eq 64 ]
}

@test "reports a missing file on stderr" {
  run "${REPO_ROOT}/bin/report.sh" "${REPO_ROOT}/data/absent.csv"
  [ "$status" -eq 66 ]
}
