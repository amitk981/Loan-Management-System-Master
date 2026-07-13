#!/usr/bin/env bash

ralph_max_repair_attempts() {
  local config="${1:?config path is required}"
  local configured=""

  configured="$(awk -F': *' '/^[[:space:]]*max_retries:/ {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' "$config" | xargs || true)"
  if [[ "$configured" =~ ^[0-9]+$ ]] && (( configured >= 1 && configured <= 5 )); then
    echo "$configured"
  else
    echo 1
  fi
}

ralph_max_progressive_repair_attempts() {
  local config="${1:?config path is required}"
  local configured=""

  configured="$(awk -F': *' '/^[[:space:]]*max_progressive_repairs:/ {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' "$config" | xargs || true)"
  if [[ "$configured" =~ ^[0-9]+$ ]] && (( configured >= 1 && configured <= 10 )); then
    echo "$configured"
  else
    # Three remains bounded but allows a normal failure followed by two newly
    # exposed failures to reach a final green validation without owner repair.
    echo 3
  fi
}
