# Formatting helpers for the provisioning configuration.
# shellcheck shell=bash

# Formats one users.conf entry.
# Arguments: account name, login shell
# Outputs: the formatted line on stdout
format_line() {
  printf '%s:%s\n' "$1" "$2"
}
