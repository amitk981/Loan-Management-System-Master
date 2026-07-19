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
      '/^## Convergence Metrics[[:space:]]*$/ {
         sections += 1
         inside = (sections == 1)
         next
       }
       /^## / { inside = 0 }
       inside && $1 == "- " label { matches += 1; value = $2 }
       END {
         if (sections == 1 && matches == 1) print value
       }' "$packet")"
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

# Return the Parent Epic numbers declared by one slice. Older fixture slices
# without metadata retain the numeric-prefix fallback, but real queue decisions
# prefer the explicit owner so CR-* maintenance work cannot be skipped.
ralph_slice_parent_epics() {
  local slice_dir="${1:?slice directory is required}" slice_id="${2:-}"
  local slice_file="$slice_dir/$slice_id.md" values=""
  if [[ -f "$slice_file" ]]; then
    values="$(awk '
      /^## Parent Epic(s)?[[:space:]]*$/ { inside = 1; next }
      inside && /^## / { exit }
      inside { print }
    ' "$slice_file" | sed -nE 's/.*Epic[[:space:]]+([0-9][0-9][0-9]).*/\1/p' \
      | sort -u)"
  fi
  if [[ -n "$values" ]]; then
    printf '%s\n' "$values"
  elif [[ "$slice_id" =~ ^([0-9][0-9][0-9]) ]]; then
    printf '%s\n' "${BASH_REMATCH[1]}"
  fi
}

ralph_queue_has_unfinished_parent_epic() {
  local slice_dir="${1:?slice directory is required}" epic="${2:-}"
  local candidate status parent
  [[ "$epic" =~ ^[0-9][0-9][0-9]$ ]] || return 1
  for candidate in "$slice_dir"/*.md; do
    [[ -f "$candidate" ]] || continue
    [[ "$(basename "$candidate")" != "architecture-review.md" ]] || continue
    status="$(awk '/^## Status/ { getline; print; exit }' "$candidate")"
    case "$status" in
      "Not Started"|Blocked) ;;
      *) continue ;;
    esac
    while IFS= read -r parent; do
      [[ "$parent" == "$epic" ]] && return 0
    done < <(ralph_slice_parent_epics "$slice_dir" "$(basename "$candidate" .md)")
  done
  return 1
}

# Return the mandatory review reason introduced by a completed slice. Explicit
# Parent Epic ownership is authoritative, including for CR-* slices. A review
# is not due while any actionable/blocked slice from the same epic remains.
ralph_architecture_review_boundary_reason() {
  local current_slice="${1:-}" next_slice="${2:-}" remaining="${3:-}"
  local slice_dir="${4:-docs/slices}" current_epic="" next_epic=""
  local remaining_line remaining_id parent
  current_epic="$(ralph_slice_parent_epics "$slice_dir" "$current_slice" | head -1)"
  if [[ -n "$current_epic" ]]; then
    while IFS= read -r remaining_line; do
      [[ -n "$remaining_line" ]] || continue
      remaining_id="${remaining_line%% (*}"
      while IFS= read -r parent; do
        [[ "$parent" == "$current_epic" ]] && return 0
      done < <(ralph_slice_parent_epics "$slice_dir" "$remaining_id")
    done <<< "$remaining"
  fi
  next_epic="$(ralph_slice_parent_epics "$slice_dir" "$next_slice" | head -1)"
  if [[ -z "$next_epic" && -n "$remaining" ]]; then
    while IFS= read -r remaining_line; do
      [[ -n "$remaining_line" ]] || continue
      remaining_id="${remaining_line%% (*}"
      next_epic="$(ralph_slice_parent_epics "$slice_dir" "$remaining_id" | head -1)"
      [[ -n "$next_epic" ]] && break
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

# Remove only boundary reasons disproved by explicit pending Parent Epic work.
# Cadence, failed-review, and completion reasons remain fail-closed. When this
# repairs a terminal-corrective false positive, retain one corrective generation
# so the eventual real epic checkpoint uses the targeted closure lane.
ralph_reconcile_architecture_review_due() {
  local state_file="${1:?state file is required}" slice_dir="${2:?slice directory is required}"
  local due reason part epic kept="" repaired_epic=""
  local boundary_pattern='^epic_boundary:([0-9][0-9][0-9])->'
  due="$(ralph_architecture_review_due "$state_file")" || return 1
  [[ "$due" == "True" ]] || return 0
reason="$(python3 - "$state_file" <<'PY'
import json, sys
print(json.load(open(sys.argv[1])).get("architecture_review_due_reason", ""))
PY
)"
  [[ -n "$reason" ]] || return 0
  IFS='+' read -r -a parts <<< "$reason"
  for part in "${parts[@]}"; do
    if [[ "$part" =~ $boundary_pattern ]]; then
      epic="${BASH_REMATCH[1]}"
      if ralph_queue_has_unfinished_parent_epic "$slice_dir" "$epic"; then
        repaired_epic="$epic"
        continue
      fi
    fi
    kept="${kept:+$kept+}$part"
  done
  [[ -n "$repaired_epic" ]] || return 0
  python3 - "$state_file" "$kept" "$repaired_epic" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
kept = sys.argv[2]
epic = sys.argv[3]
state = json.loads(path.read_text())
state["architecture_review_due"] = bool(kept)
if kept:
    state["architecture_review_due_reason"] = kept
else:
    state.pop("architecture_review_due_reason", None)
if int(state.get("last_architecture_review_metrics", {}).get("corrective_slices_added", 0)) > 0:
    state["architecture_review_cycle_epic"] = epic
    state["architecture_review_corrective_generation"] = max(
        1, int(state.get("architecture_review_corrective_generation", 0))
    )
path.write_text(json.dumps(state, indent=2) + "\n")
PY
  printf 'Reconciled premature architecture-review boundary for Epic %s; same-epic work remains.\n' \
    "$repaired_epic"
}

ralph_validate_architecture_review_convergence() {
  local config="${1:?config is required}" state_file="${2:?state file is required}"
  local added="${3:-}" maximum generation
  [[ "$added" =~ ^[0-9]+$ ]] || {
    echo "Corrective-slice addition count must be a non-negative integer." >&2
    return 1
  }
  (( added > 0 )) || return 0
  maximum="$(awk -F': *' '/^[[:space:]]*architecture_review_max_corrective_generations:/ {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' "$config" | xargs || true)"
  maximum="${maximum:-2}"
  generation="$(python3 - "$state_file" <<'PY'
import json, sys
try:
    print(max(0, int(json.load(open(sys.argv[1])).get("architecture_review_corrective_generation", 0))))
except (OSError, ValueError, TypeError, json.JSONDecodeError):
    print("invalid")
PY
)"
  if ! [[ "$maximum" =~ ^[1-9][0-9]*$ && "$generation" =~ ^[0-9]+$ ]]; then
    echo "Invalid architecture-review convergence configuration or state." >&2
    return 1
  fi
  if (( generation + 1 > maximum )); then
    echo "Architecture review exceeded the $maximum-generation corrective cap; refusing another successor." >&2
    return 1
  fi
}

ralph_architecture_review_scope_instruction() {
  local state_file="${1:?state file is required}"
  python3 - "$state_file" <<'PY'
import json, re, sys
try:
    state = json.load(open(sys.argv[1]))
except (OSError, json.JSONDecodeError):
    raise SystemExit(0)
reason = state.get("architecture_review_due_reason", "")
cycle = state.get("architecture_review_cycle_epic")
generation = int(state.get("architecture_review_corrective_generation", 0) or 0)
match = re.search(r"epic_(?:boundary|completion):([0-9]{3})", reason)
if match and cycle == match.group(1) and generation > 0:
    print(
        f"- This is targeted corrective-closure review generation {generation} for Epic {cycle}. "
        "Review only the diffs since the last successful review, the active findings already mapped "
        "to this review cycle, and their declared acceptance evidence. Do not rescan unaffected "
        "historical modules or relabel the same root-owner symptom as a new finding. At most one "
        "additional root repair may be admitted; a later recurrence must fail closed instead of "
        "creating another leaf corrective."
    )
PY
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
# `- Existing corrective slice: <ID>` lines. Existing targets may use either
# the numeric product-slice format or the CR-NNN maintenance format; they must
# already be tracked and remain Not Started or Blocked.
ralph_architecture_review_existing_corrective_count() {
  local packet="${1:?review packet is required}" worktree="${2:?worktree is required}"
  local value id matches match_count relative status head_status count=0 seen=$'\n'
  while IFS= read -r value; do
    [[ -n "$value" ]] || continue
    id="$(printf '%s' "$value" | xargs)"
    if ! [[ "$id" =~ ^([0-9][0-9][0-9][A-Za-z0-9]*|CR-[0-9][0-9][0-9][0-9]*)$ ]]; then
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
