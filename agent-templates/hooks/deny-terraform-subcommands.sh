#!/usr/bin/env bash
# PreToolUse hook for the Bash tool. Blocks a terraform or tofu invocation of any
# subcommand named as an argument, such as `apply destroy`, and allows everything else.
#
# The match is narrower than the rule it enforces. It sees the command text the agent
# wrote, so it catches `terraform apply`, `terraform -chdir=infra apply` and the same
# inside `bash -c '...'`, and misses a subcommand reached through a variable, an alias,
# a Makefile target or a wrapper script. The prose rule in the agent template still holds
# for those.
#
# Fails closed: any internal error, including jq missing or input that does not parse,
# exits 2 and blocks the command, since a hook that allows on error enforces nothing.

set -Eeuo pipefail

block() {
  printf 'deny-terraform-subcommands: %s\n' "$1" >&2
  exit 2
}

trap 'block "internal error on line ${LINENO}; blocking rather than allowing"' ERR

main() {
  local subcommand
  local input
  local command

  if [[ "$#" -eq 0 ]]; then
    block "no subcommands named in the hook configuration; name at least one, such as apply"
  fi
  for subcommand in "$@"; do
    if [[ ! "${subcommand}" =~ ^[a-z][a-z-]*$ ]]; then
      block "subcommand '${subcommand}' in the hook configuration is not a plain word"
    fi
  done

  if ! command -v jq >/dev/null 2>&1; then
    block "jq is not installed; install it, or remove this hook from the agent deliberately"
  fi

  input="$(cat)"
  command="$(jq -er '.tool_input.command // ""' <<<"${input}")"

  for subcommand in "$@"; do
    # Preceded by start of text or anything that cannot continue a word, so
    # `/usr/bin/terraform` matches and `my-terraform` does not. Global flags such as
    # `-chdir=dir` may sit between the binary and the subcommand.
    if grep -Eq "(^|[^[:alnum:]_.-])(terraform|tofu)([[:space:]]+-[^[:space:]]+)*[[:space:]]+${subcommand}([^[:alnum:]_-]|\$)" \
      <<<"${command}"; then
      block "this agent does not run 'terraform ${subcommand}'. Review the configuration \
statically and say in the summary that ${subcommand} was not run."
    fi
  done
}

main "$@"
