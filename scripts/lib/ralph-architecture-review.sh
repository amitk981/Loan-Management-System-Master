#!/usr/bin/env bash

# Ordinary architecture reviewers may change documentation and queue metadata
# only. The orchestrator writes state/progress after validation. Product or
# mechanical-state edits in review mode fail closed.

ralph_architecture_review_metrics() {
  local packet="${1:?review packet is required}"
  local closed critical high medium low added label value values=()
  [[ -s "$packet" ]] || {
    echo "Architecture review packet is missing: $packet" >&2
    return 1
  }
  for label in \
      "Findings closed" "New Critical" "New High" \
      "New Medium" "New Low" "Corrective slices added"; do
    value="$(awk -F': *' -v label="$label" \
      '$1 == "- " label { print $2; exit }' "$packet")"
    if ! [[ "$value" =~ ^[0-9]+$ ]]; then
      echo "Architecture review metric '$label' must be a non-negative integer." >&2
      return 1
    fi
    values+=("$value")
  done
  closed="${values[0]}"
  critical="${values[1]}"
  high="${values[2]}"
  medium="${values[3]}"
  low="${values[4]}"
  added="${values[5]}"
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$closed" "$critical" "$high" "$medium" "$low" "$added"
}

ralph_architecture_review_interval() {
  local config="${1:?config is required}" state_file="${2:?state file is required}"
  local base clean required streak
  base="$(awk -F': *' '/^[[:space:]]*architecture_review_every_completed_slices:/ {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' "$config" | xargs || true)"
  clean="$(awk -F': *' '/^[[:space:]]*architecture_review_clean_every_completed_slices:/ {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' "$config" | xargs || true)"
  required="$(awk -F': *' '/^[[:space:]]*architecture_review_clean_streak_required:/ {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' "$config" | xargs || true)"
  base="${base:-4}"
  clean="${clean:-$base}"
  required="${required:-2}"
  if ! [[ "$base" =~ ^[1-9][0-9]*$ && "$clean" =~ ^[1-9][0-9]*$ \
      && "$required" =~ ^[1-9][0-9]*$ ]] || (( clean < base )); then
    echo "Invalid adaptive architecture-review configuration." >&2
    return 1
  fi
  streak="$(python3 - "$state_file" <<'PY'
import json
import sys

try:
    state = json.load(open(sys.argv[1]))
    value = int(state.get("architecture_review_clean_streak", 0))
except (OSError, ValueError, TypeError, json.JSONDecodeError):
    value = 0
print(max(value, 0))
PY
)"
  if (( streak >= required )); then
    printf '%s\n' "$clean"
  else
    printf '%s\n' "$base"
  fi
}

# Print exactly True or False. Missing, malformed, or non-boolean state is an
# error so callers cannot silently skip a due review or declare completion.
ralph_architecture_review_due() {
  local state_file="${1:?state file is required}"
  python3 - "$state_file" <<'PY'
import json
import sys

try:
    with open(sys.argv[1]) as handle:
        state = json.load(handle)
except (OSError, json.JSONDecodeError) as exc:
    raise SystemExit(f"Cannot read architecture-review state: {exc}")
value = state.get("architecture_review_due")
if not isinstance(value, bool):
    raise SystemExit("architecture_review_due must be a boolean")
print("True" if value else "False")
PY
}

# Preserve an already-due mandatory review even when cadence alone would not
# fire after the next product slice. This prevents a failed epic-boundary
# review from being cleared by work in the following epic.
ralph_architecture_review_due_after_product() {
  local prior_due="${1:-}" completed="${2:-}" threshold="${3:-}"
  if ! [[ "$prior_due" == "True" || "$prior_due" == "False" ]] \
      || ! [[ "$completed" =~ ^[0-9]+$ && "$threshold" =~ ^[1-9][0-9]*$ ]]; then
    echo "Invalid architecture-review product transition inputs." >&2
    return 1
  fi
  if [[ "$prior_due" == "True" ]] || (( completed >= threshold )); then
    printf 'True\n'
  else
    printf 'False\n'
  fi
}

# Return the mandatory review reason introduced by a completed numbered slice.
# A transition to a different numbered epic is an ordinary boundary; finishing
# the last actionable slice is the final epic/project-completion boundary.
# Blocked work prevents a false final-completion checkpoint.
ralph_architecture_review_boundary_reason() {
  local current_slice="${1:-}" next_slice="${2:-}" remaining="${3:-}"
  local current_epic="" next_epic="" remaining_line
  if [[ "$current_slice" =~ ^([0-9][0-9][0-9]) ]]; then
    current_epic="${BASH_REMATCH[1]}"
  fi
  if [[ "$next_slice" =~ ^([0-9][0-9][0-9]) ]]; then
    next_epic="${BASH_REMATCH[1]}"
  fi
  if [[ -z "$next_epic" && -n "$remaining" ]]; then
    while IFS= read -r remaining_line; do
      if [[ "$remaining_line" =~ ^([0-9][0-9][0-9]) ]]; then
        next_epic="${BASH_REMATCH[1]}"
        break
      fi
    done <<< "$remaining"
  fi
  if [[ -n "$current_epic" && -n "$next_epic" && "$next_epic" != "$current_epic" ]]; then
    printf 'epic_boundary:%s->%s\n' "$current_epic" "$next_epic"
  elif [[ -n "$current_epic" && -z "$next_slice" && -z "$remaining" ]]; then
    printf 'epic_completion:%s\n' "$current_epic"
  elif [[ -z "$current_epic" && -z "$next_slice" && -z "$remaining" \
      && -n "$current_slice" ]]; then
    printf 'project_completion:%s\n' "$current_slice"
  fi
}

# Critical/High findings cannot disappear into a metrics packet. Related
# findings may share one root-owner corrective slice, so require at least one
# queued correction rather than an artificial one-finding/one-slice ratio.
ralph_validate_architecture_review_admission() {
  local critical="${1:-}" high="${2:-}" added="${3:-}" mapped="${4:-0}"
  if ! [[ "$critical" =~ ^[0-9]+$ && "$high" =~ ^[0-9]+$ \
      && "$added" =~ ^[0-9]+$ && "$mapped" =~ ^[0-9]+$ ]]; then
    echo "Architecture review admission counts must be non-negative integers." >&2
    return 1
  fi
  if (( critical + high > 0 && added + mapped == 0 )); then
    echo "Architecture review found Critical/High issues but recorded no corrective work." >&2
    return 1
  fi
}

# Count only new, executable numeric corrective slices. Any untracked slice
# file that is Complete, Superseded, non-numeric, or missing Depends On is an
# invalid architecture-review candidate rather than evidence of queue action.
ralph_architecture_review_new_corrective_count() {
  local worktree="${1:?worktree is required}" path base status count=0
  while IFS= read -r path; do
    [[ -n "$path" ]] || continue
    base="$(basename "$path")"
    if ! [[ "$base" =~ ^[0-9][0-9][0-9][A-Za-z0-9]*-.+\.md$ ]]; then
      echo "New corrective slice is not a numeric queue id: $base" >&2
      return 1
    fi
    status="$(awk '/^## Status/ { getline; print; exit }' "$worktree/$path")"
    if [[ "$status" != "Not Started" ]]; then
      echo "New corrective slice must be Not Started: $base ($status)" >&2
      return 1
    fi
    if ! grep -q '^## Depends On' "$worktree/$path"; then
      echo "New corrective slice has no Depends On contract: $base" >&2
      return 1
    fi
    count=$((count + 1))
  done < <(git -C "$worktree" ls-files --others --exclude-standard -- docs/slices)
  printf '%s\n' "$count"
}

# A new finding may already belong to one actionable root-owner slice. Review
# packets can map it without creating duplicate queue work using exact
# `- Existing corrective slice: <ID>` lines. Targets must already be tracked
# and remain Not Started or Blocked.
ralph_architecture_review_existing_corrective_count() {
  local packet="${1:?review packet is required}" worktree="${2:?worktree is required}"
  local value id matches match_count relative status head_status count=0 seen=$'\n'
  while IFS= read -r value; do
    [[ -n "$value" ]] || continue
    id="$(printf '%s' "$value" | xargs)"
    if ! [[ "$id" =~ ^[0-9][0-9][0-9][A-Za-z0-9]*$ ]]; then
      echo "Existing corrective mapping has invalid slice id: $value" >&2
      return 1
    fi
    case "$seen" in
      *$'\n'"$id"$'\n'*) continue ;;
    esac
    matches="$(find "$worktree/docs/slices" -maxdepth 1 -type f -name "${id}-*.md" | sort)"
    match_count="$(printf '%s\n' "$matches" | grep -c . || true)"
    if [[ "$match_count" != "1" ]]; then
      echo "Existing corrective mapping must resolve exactly once: $id" >&2
      return 1
    fi
    relative="${matches#"$worktree/"}"
    if ! git -C "$worktree" ls-files --error-unmatch "$relative" >/dev/null 2>&1; then
      echo "Existing corrective mapping is not an existing tracked slice: $id" >&2
      return 1
    fi
    status="$(awk '/^## Status/ { getline; print; exit }' "$matches")"
    case "$status" in
      "Not Started"|Blocked) ;;
      *)
        echo "Existing corrective mapping is not actionable: $id ($status)" >&2
        return 1
        ;;
    esac
    head_status="$(git -C "$worktree" show "HEAD:$relative" \
      | awk '/^## Status/ { getline; print; exit }')"
    case "$head_status" in
      "Not Started"|Blocked) ;;
      *)
        echo "Existing corrective mapping was not actionable before this review: $id ($head_status)" >&2
        return 1
        ;;
    esac
    seen="${seen}${id}"$'\n'
    count=$((count + 1))
  done < <(awk -F': *' '$1 == "- Existing corrective slice" { print $2 }' "$packet")
  printf '%s\n' "$count"
}

ralph_validate_architecture_review_change_scope() {
  local worktree="${1:?worktree is required}"
  local run_id="${2:?current run id is required}"
  local changed invalid=0

  if ! [[ "$run_id" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]]; then
    echo "Architecture review run id is unsafe: $run_id" >&2
    return 1
  fi

  while IFS= read -r changed; do
    [[ -n "$changed" ]] || continue
    case "$changed" in
      docs/*|.ralph/runs/"$run_id"/*)
        ;;
      *)
        echo "Architecture review may not modify product path $changed." >&2
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
