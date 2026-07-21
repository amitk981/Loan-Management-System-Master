#!/usr/bin/env bash

# Recommend the least expensive backend validation lane that still fails closed.
# The validator separately resolves whether that recommendation is authoritative
# under the configured policy.

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

ralph_backend_authoritative_lane() {
  local config="${1:?config file is required}"
  local recommendation="${2:?backend recommendation is required}"
  local policy
  policy="$(ralph_backend_config_value "$config" backend_validation_policy full)"
  if [[ "$policy" == "selective" ]]; then
    case "$recommendation" in
      skip|impacted|full) printf '%s\n' "$recommendation" ;;
      *) printf '%s\n' full ;;
    esac
  else
    printf '%s\n' full
  fi
}

ralph_backend_append_test_path() {
  local path="${1:?test path is required}"
  local existing test_label
  for existing in ${RALPH_BACKEND_TEST_PATHS[@]+"${RALPH_BACKEND_TEST_PATHS[@]}"}; do
    [[ "$existing" == "$path" ]] && return 0
  done
  RALPH_BACKEND_TEST_PATHS+=("$path")
  RALPH_BACKEND_TEST_PATH_COUNT=$((RALPH_BACKEND_TEST_PATH_COUNT + 1))
  test_label="${path%.py}"
  test_label="${test_label//\//.}"
  RALPH_BACKEND_TEST_LABELS+=("$test_label")
  RALPH_BACKEND_TEST_LABEL_COUNT=$((RALPH_BACKEND_TEST_LABEL_COUNT + 1))
}

ralph_backend_manifest_test_paths() {
  local worktree_dir="${1:?worktree directory is required}"
  local production_root="${2:?backend production root is required}"
  local backend_dir="${3:?backend directory is required}"
  python3 - "$worktree_dir" "$production_root" "$backend_dir" <<'PY'
import glob
import json
import sys
from pathlib import Path

worktree = Path(sys.argv[1]).resolve()
production_root, backend_dir = sys.argv[2:]
manifest = worktree / "scripts/config/ralph-backend-test-impact.json"
try:
    payload = json.loads(manifest.read_text())
    patterns = payload[production_root]
    if not isinstance(patterns, list) or not patterns:
        raise ValueError("empty mapping")
except (OSError, KeyError, ValueError, json.JSONDecodeError, TypeError):
    raise SystemExit(3)

paths: set[str] = set()
for pattern in patterns:
    if not isinstance(pattern, str) or not pattern.startswith(f"{backend_dir}/tests/test_"):
        raise SystemExit(3)
    for match in glob.glob(str(worktree / pattern)):
        candidate = Path(match)
        if candidate.is_file() and candidate.suffix == ".py":
            paths.add(str(candidate.relative_to(worktree)))
if not paths:
    raise SystemExit(3)
print("\n".join(sorted(paths)))
PY
}

ralph_backend_test_imports_root() {
  local test_path="${1:?test path is required}"
  local backend_dir="${2:?backend directory is required}"
  local production_root="${3:?backend production root is required}"
  python3 - "$test_path" "$backend_dir" "$production_root" <<'PY'
import ast
import sys
from pathlib import Path

path, backend, root = sys.argv[1:]
prefix = f"{backend}.{root}"
try:
    tree = ast.parse(Path(path).read_text())
except (OSError, SyntaxError, UnicodeDecodeError):
    raise SystemExit(1)
for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        if any(alias.name == prefix or alias.name.startswith(prefix + ".") for alias in node.names):
            raise SystemExit(0)
    elif isinstance(node, ast.ImportFrom):
        module = node.module or ""
        if module == prefix or module.startswith(prefix + "."):
            raise SystemExit(0)
        if module == backend and any(alias.name == root for alias in node.names):
            raise SystemExit(0)
raise SystemExit(1)
PY
}

ralph_backend_coverage_action() {
  local lane="${1:?backend validation lane is required}"
  local prerequisite_failed="${2:-0}"
  local impacted_failed="${3:-0}"
  if [[ "$lane" == "skip" ]]; then
    printf '%s\n' skip
  elif [[ "$prerequisite_failed" == "1" || "$impacted_failed" == "1" ]]; then
    printf '%s\n' defer
  elif [[ "$lane" == "impacted" ]]; then
    printf '%s\n' impacted
  else
    printf '%s\n' full
  fi
}

ralph_select_backend_validation_lane() {
  local worktree_dir="${1:?worktree directory is required}"
  local backend_dir="${2:?backend directory is required}"
  local slice_file="${3:?slice file is required}"
  local slice_id="${4:?slice id is required}"
  local config="${5:?config file is required}"
  local state_file="${6:?state file is required}"
  local policy cadence path risk_raw workers
  local changed_path_lines relative_path production_root candidate_root
  local mapped_test mapped_test_path production_path_count force_full_reason
  local manifest_paths manifest_rc

  RALPH_BACKEND_VALIDATION_LANE="full"
  RALPH_BACKEND_VALIDATION_REASON="policy failed closed before classification"
  RALPH_BACKEND_SLICE_RISK="unknown"
  RALPH_BACKEND_COMPLETION_ORDINAL="0"
  RALPH_BACKEND_IMPACTED_WORKERS="1"
  RALPH_BACKEND_CHANGED_PATHS=()
  RALPH_BACKEND_CHANGED_TEST_PATHS=()
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

  changed_path_lines="$(ralph_changed_paths "$worktree_dir")"
  while IFS= read -r path; do
    [[ -n "$path" && "$path" == "$backend_dir/"* ]] || continue
    RALPH_BACKEND_CHANGED_PATHS+=("$path")
    RALPH_BACKEND_CHANGED_COUNT=$((RALPH_BACKEND_CHANGED_COUNT + 1))
  done <<< "$changed_path_lines"

  if [[ "$policy" != "full" && "$policy" != "shadow" \
        && "$policy" != "selective" ]]; then
    RALPH_BACKEND_VALIDATION_REASON="unknown backend_validation_policy '$policy'; failed closed"
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
  production_root=""
  production_path_count=0
  force_full_reason=""
  for path in ${RALPH_BACKEND_CHANGED_PATHS[@]+"${RALPH_BACKEND_CHANGED_PATHS[@]}"}; do
    if [[ ! -e "$worktree_dir/$path" ]]; then
      force_full_reason="backend path was deleted or renamed: $path"
      continue
    fi
    if [[ "$path" == "$backend_dir/tests/test_"*.py \
          || "$path" == "$backend_dir/"*"/tests/test_"*.py ]]; then
      RALPH_BACKEND_CHANGED_TEST_PATHS+=("$path")
      ralph_backend_append_test_path "$path"
      continue
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
        force_full_reason="shared schema or backend infrastructure changed: $path"
        continue
        ;;
    esac
    relative_path="${path#"$backend_dir/"}"
    candidate_root="${relative_path%%/*}"
    if [[ "$candidate_root" == "$relative_path" ]]; then
      force_full_reason="backend package-root file changed: $path"
      continue
    fi
    case "$candidate_root" in
      common|config|core|domain|middleware|processes|shared|tests|utils)
        force_full_reason="shared backend root changed: $candidate_root"
        continue
        ;;
    esac
    if [[ -n "$production_root" && "$candidate_root" != "$production_root" ]]; then
      force_full_reason="multiple backend module roots changed: $production_root, $candidate_root"
      continue
    fi
    production_root="$candidate_root"
    production_path_count=$((production_path_count + 1))
  done

  # The impact pack is derived from production imports across the repository's
  # tests and from the maintained route/contract ownership manifest, not solely
  # from test files the implementation happened to edit. Missing ownership is
  # unsafe for selection and therefore forces the complete suite.
  if [[ -n "$production_root" ]]; then
    while IFS= read -r mapped_test_path; do
      [[ -n "$mapped_test_path" ]] || continue
      mapped_test_path="${mapped_test_path#"$worktree_dir/"}"
      ralph_backend_append_test_path "$mapped_test_path"
    done < <(rg -l --glob 'test_*.py' \
      "${backend_dir}[.]${production_root}([.]|[[:space:]])" \
      "$worktree_dir/$backend_dir" 2>/dev/null | LC_ALL=C sort -u || true)
    manifest_rc=0
    manifest_paths="$(ralph_backend_manifest_test_paths \
      "$worktree_dir" "$production_root" "$backend_dir")" || manifest_rc=$?
    if (( manifest_rc != 0 )); then
      force_full_reason="backend root $production_root has no valid owner/contract test mapping"
    else
      while IFS= read -r mapped_test_path; do
        [[ -n "$mapped_test_path" ]] \
          && ralph_backend_append_test_path "$mapped_test_path"
      done <<< "$manifest_paths"
    fi
  fi

  if [[ "$policy" == "full" ]]; then
    RALPH_BACKEND_VALIDATION_REASON="backend_validation_policy is full"
    return 0
  fi
  if (( RALPH_BACKEND_COMPLETION_ORDINAL % cadence == 0 )); then
    RALPH_BACKEND_VALIDATION_REASON="periodic full-suite checkpoint at completed slice $RALPH_BACKEND_COMPLETION_ORDINAL"
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
  if [[ -n "$force_full_reason" ]]; then
    RALPH_BACKEND_VALIDATION_REASON="$force_full_reason"
    return 0
  fi

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
    for path in ${RALPH_BACKEND_CHANGED_TEST_PATHS[@]+"${RALPH_BACKEND_CHANGED_TEST_PATHS[@]}"}; do
      if ralph_backend_test_imports_root \
          "$worktree_dir/$path" "$backend_dir" "$production_root"; then
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
