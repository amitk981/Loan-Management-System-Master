#!/usr/bin/env bash

RALPH_CAPABILITY_POSTGRESQL_FIVE_RACE_ACCEPTANCE="postgresql-five-race-acceptance"
RALPH_CAPABILITY_LOCALHOST_E2E_SERVER="localhost-e2e-server"

ralph_slice_capabilities() {
  local slice_file="${1:?slice file is required}"
  [[ -f "$slice_file" ]] || return 0

  awk '
    $0 == "## Runtime Capabilities" { in_capabilities = 1; next }
    in_capabilities && /^## / { exit }
    in_capabilities {
      line = $0
      sub(/^[[:space:]]*-[[:space:]]*/, "", line)
      gsub(/`/, "", line)
      sub(/[[:space:]]*#.*/, "", line)
      sub(/^[[:space:]]+/, "", line)
      sub(/[[:space:]]+$/, "", line)
      if (length(line) > 0) print line
    }
  ' "$slice_file"
}

ralph_validate_slice_capabilities() {
  local slice_file="${1:?slice file is required}"
  local capability=""

  while IFS= read -r capability; do
    case "$capability" in
      none|"$RALPH_CAPABILITY_POSTGRESQL_FIVE_RACE_ACCEPTANCE"|"$RALPH_CAPABILITY_LOCALHOST_E2E_SERVER")
        ;;
      *)
        echo "Unknown Ralph runtime capability '$capability' in $slice_file; refusing to continue." >&2
        return 1
        ;;
    esac
  done < <(ralph_slice_capabilities "$slice_file")
}

ralph_slice_has_capability() {
  local slice_file="${1:?slice file is required}"
  local expected="${2:?capability is required}"
  local capability=""

  while IFS= read -r capability; do
    [[ "$capability" == "$expected" ]] && return 0
  done < <(ralph_slice_capabilities "$slice_file")
  return 1
}

ralph_codex_permission_profile_for_slice() {
  local slice_file="${1:?slice file is required}"
  ralph_validate_slice_capabilities "$slice_file" || return 1

  local needs_postgres=false
  local needs_localhost=false
  ralph_slice_has_capability "$slice_file" "$RALPH_CAPABILITY_POSTGRESQL_FIVE_RACE_ACCEPTANCE" && needs_postgres=true
  ralph_slice_has_capability "$slice_file" "$RALPH_CAPABILITY_LOCALHOST_E2E_SERVER" && needs_localhost=true

  if [[ "$needs_postgres" == true && "$needs_localhost" == true ]]; then
    echo "ralph-postgres-localhost"
  elif [[ "$needs_postgres" == true ]]; then
    echo "ralph-postgres"
  elif [[ "$needs_localhost" == true ]]; then
    echo "ralph-localhost"
  else
    echo ":workspace"
  fi
}
