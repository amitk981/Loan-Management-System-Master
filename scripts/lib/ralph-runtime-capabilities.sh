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
  local capability_count=0
  local header_count=0
  local none_count=0
  local seen_capabilities=""
  local problem_count=0

  if [[ ! -f "$slice_file" ]]; then
    echo "Slice file does not exist: $slice_file" >&2
    return 1
  fi

  header_count="$(grep -c '^## Runtime Capabilities$' "$slice_file" || true)"
  if [[ "$header_count" != "1" ]]; then
    echo "Slice $slice_file must declare exactly one '## Runtime Capabilities' section (found $header_count)." >&2
    problem_count=$((problem_count + 1))
  fi

  while IFS= read -r capability; do
    capability_count=$((capability_count + 1))
    case "$capability" in
      none)
        none_count=$((none_count + 1))
        ;;
      "$RALPH_CAPABILITY_POSTGRESQL_FIVE_RACE_ACCEPTANCE"|"$RALPH_CAPABILITY_LOCALHOST_E2E_SERVER")
        ;;
      *)
        echo "Unknown Ralph runtime capability '$capability' in $slice_file; refusing to continue." >&2
        problem_count=$((problem_count + 1))
        ;;
    esac
    if printf '%s\n' "$seen_capabilities" | grep -Fxq "$capability"; then
      echo "Duplicate Ralph runtime capability '$capability' in $slice_file." >&2
      problem_count=$((problem_count + 1))
    else
      seen_capabilities="${seen_capabilities}${seen_capabilities:+$'\n'}${capability}"
    fi
  done < <(ralph_slice_capabilities "$slice_file")

  if (( capability_count == 0 )); then
    echo "Slice $slice_file must declare 'none' or at least one supported runtime capability." >&2
    problem_count=$((problem_count + 1))
  fi
  if (( none_count > 0 && capability_count > 1 )); then
    echo "Runtime capability 'none' must be the only declaration in $slice_file." >&2
    problem_count=$((problem_count + 1))
  fi

  (( problem_count == 0 ))
}

ralph_slice_requires_postgresql_capability() {
  local slice_file="${1:?slice file is required}"
  grep -qiE 'postgresql|select_for_update|row[- ](level[- ])?lock|database[- ]lock(ing)?|(^|[^[:alnum:]_])(race|races|contention)([^[:alnum:]_]|$)' "$slice_file"
}

ralph_slice_requires_browser_capability() {
  local slice_file="${1:?slice file is required}"
  grep -qiE 'screenshot|playwright|trusted browser|real[- ]browser|browser acceptance' "$slice_file"
}

# Preflight semantic lint: a slice cannot promise trusted environment evidence
# while selecting the ordinary workspace-only sandbox. Full entry/path checks
# remain in the PostgreSQL and browser acceptance helpers.
ralph_validate_slice_runtime_requirements() {
  local slice_file="${1:?slice file is required}"
  local problem_count=0
  local postgresql_heading_count=0
  local browser_heading_count=0

  ralph_validate_slice_capabilities "$slice_file" || return 1

  postgresql_heading_count="$(grep -c '^## Trusted PostgreSQL Acceptance$' "$slice_file" || true)"
  browser_heading_count="$(grep -c '^## Trusted Browser Acceptance$' "$slice_file" || true)"

  if ralph_slice_requires_postgresql_capability "$slice_file" \
      && ! ralph_slice_has_capability "$slice_file" "$RALPH_CAPABILITY_POSTGRESQL_FIVE_RACE_ACCEPTANCE"; then
    echo "Slice $slice_file promises PostgreSQL/concurrency evidence without '$RALPH_CAPABILITY_POSTGRESQL_FIVE_RACE_ACCEPTANCE'." >&2
    problem_count=$((problem_count + 1))
  fi
  if ralph_slice_requires_browser_capability "$slice_file" \
      && ! ralph_slice_has_capability "$slice_file" "$RALPH_CAPABILITY_LOCALHOST_E2E_SERVER"; then
    echo "Slice $slice_file promises browser/screenshot evidence without '$RALPH_CAPABILITY_LOCALHOST_E2E_SERVER'." >&2
    problem_count=$((problem_count + 1))
  fi

  if ralph_slice_has_capability "$slice_file" "$RALPH_CAPABILITY_POSTGRESQL_FIVE_RACE_ACCEPTANCE" \
      && [[ "$postgresql_heading_count" != "1" ]]; then
    echo "Slice $slice_file declares PostgreSQL acceptance but must contain exactly one '## Trusted PostgreSQL Acceptance' section." >&2
    problem_count=$((problem_count + 1))
  fi
  if ralph_slice_has_capability "$slice_file" "$RALPH_CAPABILITY_LOCALHOST_E2E_SERVER" \
      && [[ "$browser_heading_count" != "1" ]]; then
    echo "Slice $slice_file declares localhost E2E but must contain exactly one '## Trusted Browser Acceptance' section." >&2
    problem_count=$((problem_count + 1))
  fi

  (( problem_count == 0 ))
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
  # Permission selection is deliberately limited to the already-validated
  # declaration. ralph-run/ralph-validate own the richer contract preflight.
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
