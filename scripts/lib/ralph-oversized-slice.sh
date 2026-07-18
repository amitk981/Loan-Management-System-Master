#!/usr/bin/env bash

# Print one trusted oversized-slice request as four tab-separated fields:
# slice id, failed run id, measured lines, configured limit. The request is
# accepted only from the run directory named by a resumable repair context;
# agent transcript text is never parsed for loop control.
ralph_oversized_slice_request() {
  local repo_root="${1:?repository root is required}"
  local context_file="${2:?repair context is required}"
  local run_id worktree slice_id marker

  declare -F ralph_repair_context_is_resumable >/dev/null || return 1
  ralph_repair_context_is_resumable "$repo_root" "$context_file" || return 1

  run_id="$(ralph_repair_context_value "$context_file" run_id)" || return 1
  worktree="$(ralph_repair_context_value "$context_file" worktree)" || return 1
  slice_id="$(ralph_repair_context_value "$context_file" slice_id)" || return 1
  marker="$worktree/.ralph/runs/$run_id/oversized-slice-request.json"
  [[ -f "$marker" ]] || return 1

  python3 - "$marker" "$run_id" "$slice_id" <<'PY'
import json
import re
import sys
from pathlib import Path

marker = Path(sys.argv[1])
expected_run_id = sys.argv[2]
expected_slice_id = sys.argv[3]

try:
    request = json.loads(marker.read_text())
    version = request["version"]
    reason = request["reason"]
    run_id = request["run_id"]
    slice_id = request["slice_id"]
    total_lines = int(request["total_lines"])
    max_lines = int(request["max_lines"])
except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
    raise SystemExit(1)

if (
    version != 1
    or reason != "diff_limit_exceeded"
    or run_id != expected_run_id
    or slice_id != expected_slice_id
    or max_lines < 1
    or total_lines <= max_lines
):
    raise SystemExit(1)

canonical_slice_id = slice_id.split("-", 1)[0]
if not re.fullmatch(r"[A-Za-z0-9]+", canonical_slice_id):
    raise SystemExit(1)

print(f"{canonical_slice_id}\t{run_id}\t{total_lines}\t{max_lines}")
PY
}

# Return the trusted failed planning run id and normalized failure signature
# for one bounded corrective oversized-slice rewrite. A context for any other
# slice, stale worktree, or unregistered branch is rejected before recovery.
ralph_oversized_split_retry_context() {
  local repo_root="${1:?repository root is required}"
  local context_file="${2:?repair context is required}"
  local expected_slice_id="${3:?oversized slice id is required}"
  local context_slice_id canonical_slice_id run_id failure_signature failure_summary split_results

  [[ "$expected_slice_id" =~ ^[A-Za-z0-9]+$ ]] || return 1
  declare -F ralph_repair_context_is_resumable >/dev/null || return 1
  ralph_repair_context_is_resumable "$repo_root" "$context_file" || return 1

  context_slice_id="$(ralph_repair_context_value "$context_file" slice_id)" || return 1
  canonical_slice_id="${context_slice_id%%-*}"
  [[ "$canonical_slice_id" == "$expected_slice_id" ]] || return 1

  run_id="$(ralph_repair_context_value "$context_file" run_id)" || return 1
  failure_signature="$(ralph_repair_context_value "$context_file" failure_signature)" || return 1
  failure_summary="$(ralph_repair_context_value "$context_file" failure_summary)" || return 1
  split_results="$(dirname "$failure_summary")/oversized-slice-split-results.md"
  [[ -f "$split_results" ]] || return 1
  grep -qF 'oversized-slice-split-results.md' "$failure_summary" || return 1
  grep -qF 'FAIL:' "$split_results" || return 1
  [[ -n "$run_id" && -n "$failure_signature" ]] || return 1
  printf '%s\t%s\n' "$run_id" "$failure_signature"
}

# Retry only a failed independent planning validation, never a successful
# candidate whose merge failed or a repeatedly failing corrective attempt.
ralph_oversized_split_retry_allowed() {
  local status="${1:?status is required}"
  local attempt="${2:?attempt is required}"
  local max_attempts="${3:?max attempts is required}"
  local failed_status="${RALPH_EXIT_FAILED:-1}"

  [[ "$status" =~ ^[0-9]+$ && "$attempt" =~ ^[0-9]+$ && "$max_attempts" =~ ^[0-9]+$ ]] \
    || return 1
  (( attempt >= 1 && max_attempts >= 1 )) || return 1
  (( status == failed_status && attempt < max_attempts ))
}

_ralph_slice_dependencies_from_stdin() {
  awk '
    /^## Depends On/ { in_section = 1; next }
    in_section && /^## / { exit }
    in_section && /^- / { if (tolower($2) != "none") print $2 }
  '
}

_ralph_dependency_list_contains() {
  local dependency_list="$1" expected="$2"
  printf '%s\n' "$dependency_list" | grep -Fxq "$expected"
}

# Split planning is allowed to reshape queue metadata only. This invariant is
# what makes it safe to validate the planning run without re-running product
# build/test/coverage gates: any production, configuration, or source change
# makes the queue rewrite fail before commit.
ralph_validate_oversized_split_change_scope() {
  local worktree="${1:?worktree is required}"
  local original_id="${2:?original slice id is required}"
  local changed changed_base baseline_deps invalid=0

  while IFS= read -r changed; do
    [[ -n "$changed" ]] || continue
    case "$changed" in
      .ralph/*|docs/working/HANDOFF.md|docs/working/ASSUMPTIONS.md|docs/working/IMPLEMENTATION_SLICE_INDEX.md|docs/working/digests/*.md)
        ;;
      docs/slices/*.md)
        changed_base="$(basename "$changed")"
        case "$changed_base" in
          "${original_id}-"*.md|"${original_id}"[A-Z]-*.md)
            continue
            ;;
        esac
        baseline_deps="$(git -C "$worktree" show "HEAD:$changed" 2>/dev/null \
          | _ralph_slice_dependencies_from_stdin || true)"
        if _ralph_dependency_list_contains "$baseline_deps" "$original_id"; then
          continue
        fi
        echo "Oversized-slice planning may not rewrite unrelated slice $changed." >&2
        invalid=1
        ;;
      *)
        echo "Oversized-slice planning may not modify $changed." >&2
        invalid=1
        ;;
    esac
  done < <(
    {
      git -C "$worktree" diff --name-only --no-renames HEAD --
      git -C "$worktree" ls-files --others --exclude-standard
    } | sort -u
  )

  (( invalid == 0 ))
}

# Validate an uncommitted queue rewrite for one oversized slice against the
# committed queue at HEAD. Successors must form a dependency-ordered chain,
# inherit the original prerequisites, and replace the original id in every
# downstream dependency that existed before the split.
ralph_validate_oversized_slice_split() {
  local worktree="${1:?worktree is required}"
  local original_id="${2:?original slice id is required}"
  local slices_rel="${3:-docs/slices}"
  local slices_dir="$worktree/$slices_rel"
  local original_file successor_list successor_count first_file first_deps
  local original_rel original_deps prerequisite previous_id successor successor_id successor_deps
  local baseline_file baseline_deps current_file current_deps terminal_id

  declare -F ralph_slice_status >/dev/null || return 1
  declare -F ralph_slice_dependencies >/dev/null || return 1

  original_file="$(find "$slices_dir" -maxdepth 1 -type f -name "${original_id}-*.md" | sort | head -n 1)"
  if [[ -z "$original_file" || "$(ralph_slice_status "$original_file")" != "Superseded" ]]; then
    echo "Oversized slice $original_id must be marked Superseded." >&2
    return 1
  fi

  successor_list="$(find "$slices_dir" -maxdepth 1 -type f -name "${original_id}[A-Z]-*.md" | sort)"
  successor_count="$(printf '%s\n' "$successor_list" | grep -c . || true)"
  if (( successor_count < 2 )); then
    echo "Oversized slice $original_id requires at least two successor slices." >&2
    return 1
  fi

  original_rel="$slices_rel/$(basename "$original_file")"
  original_deps="$(git -C "$worktree" show "HEAD:$original_rel" | _ralph_slice_dependencies_from_stdin)" || return 1
  first_file="$(printf '%s\n' "$successor_list" | head -n 1)"
  first_deps="$(ralph_slice_dependencies "$first_file")"
  while IFS= read -r prerequisite; do
    [[ -z "$prerequisite" ]] && continue
    if ! _ralph_dependency_list_contains "$first_deps" "$prerequisite"; then
      echo "First successor does not inherit prerequisite $prerequisite from $original_id." >&2
      return 1
    fi
  done <<< "$original_deps"

  previous_id=""
  while IFS= read -r successor; do
    [[ -n "$successor" ]] || continue
    successor_id="$(basename "$successor")"
    successor_id="${successor_id%%-*}"
    if [[ "$(ralph_slice_status "$successor")" != "Not Started" ]]; then
      echo "Successor $successor_id must start as Not Started." >&2
      return 1
    fi
    if ! grep -qF "Oversized slice: \`$original_id\`" "$successor"; then
      echo "Successor $successor_id does not identify oversized origin $original_id." >&2
      return 1
    fi
    successor_deps="$(ralph_slice_dependencies "$successor")"
    if [[ -n "$previous_id" ]] && ! _ralph_dependency_list_contains "$successor_deps" "$previous_id"; then
      echo "Successor $successor_id must depend on preceding successor $previous_id." >&2
      return 1
    fi
    if _ralph_dependency_list_contains "$successor_deps" "$original_id"; then
      echo "Successor $successor_id must not bypass prerequisites through superseded $original_id." >&2
      return 1
    fi
    previous_id="$successor_id"
  done <<< "$successor_list"
  terminal_id="$previous_id"

  while IFS= read -r baseline_file; do
    [[ -n "$baseline_file" || "$baseline_file" == "$original_rel" ]] || continue
    baseline_deps="$(git -C "$worktree" show "HEAD:$baseline_file" | _ralph_slice_dependencies_from_stdin)" || return 1
    _ralph_dependency_list_contains "$baseline_deps" "$original_id" || continue
    current_file="$worktree/$baseline_file"
    [[ -f "$current_file" ]] || {
      echo "Downstream slice $baseline_file disappeared during split." >&2
      return 1
    }
    current_deps="$(ralph_slice_dependencies "$current_file")"
    if _ralph_dependency_list_contains "$current_deps" "$original_id" \
        || ! _ralph_dependency_list_contains "$current_deps" "$terminal_id"; then
      echo "Downstream slice $baseline_file must replace $original_id with terminal successor $terminal_id." >&2
      return 1
    fi
  done < <(git -C "$worktree" ls-tree -r --name-only HEAD -- "$slices_rel")

  return 0
}
