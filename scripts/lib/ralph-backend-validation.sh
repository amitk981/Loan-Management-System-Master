#!/usr/bin/env bash

# Recommend the least expensive backend validation lane that still fails closed.
# The recommendation is shadow evidence only: the authoritative validator keeps
# running its configured full gates until the binding quality policy is changed.

ralph_backend_config_value() {
  local config="${1:?config file is required}"
  local key="${2:?config key is required}"
  local fallback="${3:-}"
  local value
  value="$(awk -F': *' -v key="$key" \
    '$1 ~ "^[[:space:]]*" key "$" {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' \
    "$config" | tr -d '"' | xargs || true)"
  printf '%s\n' "${value:-$fallback}"
}

ralph_backend_candidate_ordinal() {
  local state_file="${1:?state file is required}"
  local slice_id="${2:?slice id is required}"
  python3 - "$state_file" "$slice_id" <<'PY'
import json
import sys
from pathlib import Path

try:
    state = json.loads(Path(sys.argv[1]).read_text())
    completed = state.get("completed_slices", [])
    if not isinstance(completed, list):
        raise ValueError("completed_slices is not a list")
    print(len(completed) if sys.argv[2] in completed else len(completed) + 1)
except (OSError, ValueError, json.JSONDecodeError):
    print(0)
PY
}

ralph_select_backend_validation_lane() {
  local worktree_dir="${1:?worktree directory is required}"
  local backend_dir="${2:?backend directory is required}"
  local slice_file="${3:?slice file is required}"
  local slice_id="${4:?slice id is required}"
  local config="${5:?config file is required}"
  local state_file="${6:?state file is required}"
  local policy cadence path risk_raw test_label workers
  local existing_test_label test_label_seen
  local changed_path_lines relative_path production_root candidate_root
  local mapped_test production_path_count

  RALPH_BACKEND_VALIDATION_LANE="full"
  RALPH_BACKEND_VALIDATION_REASON="policy failed closed before classification"
  RALPH_BACKEND_SLICE_RISK="unknown"
  RALPH_BACKEND_COMPLETION_ORDINAL="0"
  RALPH_BACKEND_IMPACTED_WORKERS="1"
  RALPH_BACKEND_CHANGED_PATHS=()
  RALPH_BACKEND_TEST_LABELS=()
  RALPH_BACKEND_TEST_PATHS=()
  RALPH_BACKEND_CHANGED_COUNT=0
  RALPH_BACKEND_TEST_LABEL_COUNT=0
  RALPH_BACKEND_TEST_PATH_COUNT=0

  policy="$(ralph_backend_config_value "$config" backend_validation_policy full)"
  cadence="$(ralph_backend_config_value \
    "$config" backend_full_suite_every_completed_slices 4)"
  workers="$(ralph_backend_config_value "$config" backend_impacted_parallel_workers 1)"
  RALPH_BACKEND_IMPACTED_WORKERS="$workers"

  risk_raw="$(awk '/^## Risk Level[[:space:]]*$/ {getline; print; exit}' \
    "$slice_file" | xargs || true)"
  RALPH_BACKEND_SLICE_RISK="$(printf '%s' "${risk_raw:-unknown}" \
    | tr '[:upper:]' '[:lower:]')"
  RALPH_BACKEND_COMPLETION_ORDINAL="$(ralph_backend_candidate_ordinal \
    "$state_file" "$slice_id")"

  changed_path_lines="$(
    git -C "$worktree_dir" status --porcelain=v1 --untracked-files=all \
      | sed -E 's/^.{3}//; s/.* -> //; s/^"//; s/"$//'
  )"
  while IFS= read -r path; do
    [[ -n "$path" && "$path" == "$backend_dir/"* ]] || continue
    RALPH_BACKEND_CHANGED_PATHS+=("$path")
    RALPH_BACKEND_CHANGED_COUNT=$((RALPH_BACKEND_CHANGED_COUNT + 1))
  done <<< "$changed_path_lines"

  if [[ "$policy" == "full" ]]; then
    RALPH_BACKEND_VALIDATION_REASON="backend_validation_policy is full"
    return 0
  fi
  if [[ "$policy" != "shadow" ]]; then
    RALPH_BACKEND_VALIDATION_REASON="unknown backend_validation_policy '$policy'; failed closed"
    return 0
  fi

  if (( RALPH_BACKEND_CHANGED_COUNT == 0 )); then
    RALPH_BACKEND_VALIDATION_LANE="skip"
    RALPH_BACKEND_VALIDATION_REASON="candidate changes no backend path"
    return 0
  fi

  if [[ "$RALPH_BACKEND_SLICE_RISK" == "high" ]]; then
    RALPH_BACKEND_VALIDATION_REASON="high-risk backend slice"
    return 0
  fi
  if [[ "$RALPH_BACKEND_SLICE_RISK" != "low" \
        && "$RALPH_BACKEND_SLICE_RISK" != "medium" ]]; then
    RALPH_BACKEND_VALIDATION_REASON="missing or unrecognized risk level; failed closed"
    return 0
  fi
  if ! [[ "$cadence" =~ ^[1-9][0-9]*$ ]]; then
    RALPH_BACKEND_VALIDATION_REASON="invalid full-suite checkpoint cadence; failed closed"
    return 0
  fi
  if ! [[ "$workers" =~ ^[1-9][0-9]*$ ]]; then
    RALPH_BACKEND_VALIDATION_REASON="invalid impacted-test worker count; failed closed"
    return 0
  fi
  if ! [[ "$RALPH_BACKEND_COMPLETION_ORDINAL" =~ ^[1-9][0-9]*$ ]]; then
    RALPH_BACKEND_VALIDATION_REASON="invalid completion ordinal; failed closed"
    return 0
  fi
  if (( RALPH_BACKEND_COMPLETION_ORDINAL % cadence == 0 )); then
    RALPH_BACKEND_VALIDATION_REASON="periodic full-suite checkpoint at completed slice $RALPH_BACKEND_COMPLETION_ORDINAL"
    return 0
  fi

  production_root=""
  production_path_count=0
  for path in ${RALPH_BACKEND_CHANGED_PATHS[@]+"${RALPH_BACKEND_CHANGED_PATHS[@]}"}; do
    if [[ ! -e "$worktree_dir/$path" ]]; then
      RALPH_BACKEND_VALIDATION_REASON="backend path was deleted or renamed: $path"
      return 0
    fi
    case "$path" in
      "$backend_dir"/requirements*.txt|\
      "$backend_dir"/manage.py|\
      "$backend_dir"/config/*|\
      */migrations/*|\
      */models.py|\
      */models/*|\
      */settings.py|\
      */settings_*.py|\
      */apps.py|\
      */urls.py|\
      "$backend_dir"/tests/api_contracts.py)
        RALPH_BACKEND_VALIDATION_REASON="shared schema or backend infrastructure changed: $path"
        return 0
        ;;
    esac
    if [[ "$path" == "$backend_dir/tests/test_"*.py \
          || "$path" == "$backend_dir/"*"/tests/test_"*.py ]]; then
      RALPH_BACKEND_TEST_PATHS+=("$path")
      RALPH_BACKEND_TEST_PATH_COUNT=$((RALPH_BACKEND_TEST_PATH_COUNT + 1))
      test_label="${path%.py}"
      test_label="${test_label//\//.}"
      test_label_seen=0
      for existing_test_label in \
        ${RALPH_BACKEND_TEST_LABELS[@]+"${RALPH_BACKEND_TEST_LABELS[@]}"}; do
        if [[ "$existing_test_label" == "$test_label" ]]; then
          test_label_seen=1
        fi
      done
      if (( test_label_seen == 0 )); then
        RALPH_BACKEND_TEST_LABELS+=("$test_label")
        RALPH_BACKEND_TEST_LABEL_COUNT=$((RALPH_BACKEND_TEST_LABEL_COUNT + 1))
      fi
      continue
    fi

    relative_path="${path#"$backend_dir/"}"
    candidate_root="${relative_path%%/*}"
    if [[ "$candidate_root" == "$relative_path" ]]; then
      RALPH_BACKEND_VALIDATION_REASON="backend package-root file changed: $path"
      return 0
    fi
    case "$candidate_root" in
      common|config|core|domain|middleware|processes|shared|tests|utils)
        RALPH_BACKEND_VALIDATION_REASON="shared backend root changed: $candidate_root"
        return 0
        ;;
    esac
    if [[ -n "$production_root" && "$candidate_root" != "$production_root" ]]; then
      RALPH_BACKEND_VALIDATION_REASON="multiple backend module roots changed: $production_root, $candidate_root"
      return 0
    fi
    production_root="$candidate_root"
    production_path_count=$((production_path_count + 1))
  done

  if (( RALPH_BACKEND_TEST_LABEL_COUNT == 0 )); then
    RALPH_BACKEND_VALIDATION_REASON="backend changed without an explicit changed test module; failed closed"
    return 0
  fi
  if (( production_path_count > 8 )); then
    RALPH_BACKEND_VALIDATION_REASON="broad backend change touched $production_path_count production paths"
    return 0
  fi
  if [[ -n "$production_root" ]]; then
    mapped_test=0
    for path in ${RALPH_BACKEND_TEST_PATHS[@]+"${RALPH_BACKEND_TEST_PATHS[@]}"}; do
      if rg -q "${backend_dir}[.]${production_root}([.]|[[:space:]])" \
          "$worktree_dir/$path"; then
        mapped_test=1
      fi
    done
    if (( mapped_test == 0 )); then
      RALPH_BACKEND_VALIDATION_REASON="changed tests do not prove a mapping to backend root $production_root"
      return 0
    fi
  fi

  RALPH_BACKEND_VALIDATION_LANE="impacted"
  RALPH_BACKEND_VALIDATION_REASON="localized low/medium-risk backend change with explicit test modules"
}
