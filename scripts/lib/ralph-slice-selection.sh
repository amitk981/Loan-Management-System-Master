#!/usr/bin/env bash

# Slice files follow the to-issues standard: each declares its blockers under
# "## Depends On", and a slice is grabbable only when every blocker is done.
# Selection therefore walks the sorted queue and takes the first `Not Started`
# slice whose declared dependencies are all Complete or Superseded.

ralph_slice_status() {
  awk '/^## Status/ { getline; print; exit }' "${1:?slice file is required}"
}

# Restore the selected slice's orchestrator-owned Status from worktree HEAD.
# Preserve valid agent sharpening/content, but if the rejected attempt deleted
# the file or removed its Status contract, restore the full trusted slice so a
# repair agent can start instead of failing before launch.
ralph_restore_selected_slice_status() {
  local worktree="${1:?worktree is required}" relative="${2:?slice path is required}"
  local candidate="$worktree/$relative" trusted_status candidate_status
  local resolved_worktree resolved_parent expected_parent
  [[ "$relative" =~ ^docs/slices/[A-Za-z0-9._-]+\.md$ ]] || {
    echo "Selected slice restore path is unsafe: $relative" >&2
    return 1
  }
  resolved_worktree="$(cd "$worktree" && pwd -P)" || return 1
  [[ ! -L "$worktree/docs" && ! -L "$worktree/docs/slices" \
      && -d "$worktree/docs/slices" ]] || {
    echo "Selected slice parent is not a trusted worktree directory." >&2
    return 1
  }
  resolved_parent="$(cd "$worktree/docs/slices" && pwd -P)" || return 1
  expected_parent="$resolved_worktree/docs/slices"
  [[ "$resolved_parent" == "$expected_parent" ]] || {
    echo "Selected slice parent escapes the worktree: $resolved_parent" >&2
    return 1
  }
  trusted_status="$(git -C "$worktree" show "HEAD:$relative" \
    | awk '/^## Status/ { getline; print; exit }')" || return 1
  [[ -n "$trusted_status" ]] || {
    echo "Trusted selected slice has no Status contract: $relative" >&2
    return 1
  }
  candidate_status=""
  if [[ -f "$candidate" && ! -L "$candidate" ]]; then
    candidate_status="$(ralph_slice_status "$candidate")"
  elif [[ -e "$candidate" && ! -L "$candidate" ]]; then
    echo "Selected slice candidate is not a regular file: $candidate" >&2
    return 1
  fi
  if [[ ! -f "$candidate" || -L "$candidate" || -z "$candidate_status" ]]; then
    rm -f -- "$candidate" || return 1
    git -C "$worktree" show "HEAD:$relative" > "$candidate"
    return 0
  fi
  python3 - "$candidate" "$trusted_status" <<'PY'
import os
import sys
import tempfile
from pathlib import Path

path = Path(sys.argv[1])
lines = path.read_text().splitlines()
for index, line in enumerate(lines):
    if line.strip() == "## Status" and index + 1 < len(lines):
        lines[index + 1] = sys.argv[2]
        break
else:
    raise SystemExit(f"Selected slice has no Status section: {path}")
with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False) as handle:
    handle.write("\n".join(lines) + "\n")
    temporary = handle.name
os.chmod(temporary, 0o644)
os.replace(temporary, path)
PY
}

# Materialize trusted integration state/progress as regular files. Removing
# the exact candidate paths first breaks malicious symlinks or hard links
# instead of following them during repair startup.
ralph_restore_worktree_bookkeeping() {
  local trusted="${1:?trusted repository is required}" worktree="${2:?worktree is required}"
  local resolved_worktree resolved_meta relative source destination
  resolved_worktree="$(cd "$worktree" && pwd -P)" || return 1
  [[ ! -L "$worktree/.ralph" && -d "$worktree/.ralph" ]] || {
    echo "Worktree .ralph directory is missing or symlinked." >&2
    return 1
  }
  resolved_meta="$(cd "$worktree/.ralph" && pwd -P)" || return 1
  [[ "$resolved_meta" == "$resolved_worktree/.ralph" ]] || {
    echo "Worktree .ralph directory escapes the worktree." >&2
    return 1
  }
  for relative in .ralph/state.json .ralph/progress.md; do
    source="$trusted/$relative"
    destination="$worktree/$relative"
    [[ -f "$source" && ! -L "$source" ]] || {
      echo "Trusted bookkeeping source is not a regular file: $source" >&2
      return 1
    }
    if [[ -e "$destination" && ! -f "$destination" && ! -L "$destination" ]]; then
      echo "Worktree bookkeeping destination is not a file: $destination" >&2
      return 1
    fi
    rm -f -- "$destination" || return 1
    cp "$source" "$destination" || return 1
  done
}

ralph_slice_epic() {
  local slice_id="${1:-}"
  if [[ "$slice_id" =~ ^([0-9][0-9][0-9]) ]]; then
    printf '%s\n' "${BASH_REMATCH[1]}"
  fi
}

# Print tab-separated product queue counts in this order:
# Complete, Not Started, Blocked, Superseded, actionable total. Superseded
# history is reported separately and excluded from the denominator. The documentation-only
# architecture-review pseudo-slice is deliberately excluded so product
# progress matches .ralph/state.json and owner ETAs.
ralph_queue_status_counts() {
  local slices_dir="${1:-docs/slices}" file base slice_status
  local complete=0 not_started=0 blocked=0 superseded=0 actionable_total=0
  for file in "$slices_dir"/*.md; do
    [[ -f "$file" ]] || continue
    base="$(basename "$file")"
    [[ "$base" == "architecture-review.md" ]] && continue
    slice_status="$(ralph_slice_status "$file")"
    case "$slice_status" in
      Complete) complete=$((complete + 1)) ;;
      "Not Started") not_started=$((not_started + 1)) ;;
      Blocked) blocked=$((blocked + 1)) ;;
      Superseded) superseded=$((superseded + 1)) ;;
      *) continue ;;
    esac
  done
  actionable_total=$((complete + not_started + blocked))
  printf '%s\t%s\t%s\t%s\t%s\n' \
    "$complete" "$not_started" "$blocked" "$superseded" "$actionable_total"
}

# Print the dependency ids declared in a slice file, one per line. Entries are
# "- <ID>" with optional annotation text after the id; "- None" declares no
# blockers. Prose lines inside the section are commentary, not dependencies.
ralph_slice_dependencies() {
  awk '
    /^## Depends On/ { in_section = 1; next }
    in_section && /^## /   { exit }
    in_section && /^- /    { if (tolower($2) != "none") print $2 }
  ' "${1:?slice file is required}"
}

# Succeed silently when every dependency of the slice is Complete or
# Superseded. Otherwise print the unmet ids (one per line) and return 1.
# A dependency with no matching slice file is unmet: a dangling reference
# must hold the slice back, not silently unblock it.
ralph_slice_unmet_dependencies() {
  local slice_file="${1:?slice file is required}" slices_dir="${2:-docs/slices}"
  local dep dep_file unmet=()
  while IFS= read -r dep; do
    [[ -n "$dep" ]] || continue
    dep_file="$(find "$slices_dir" -maxdepth 1 -type f -name "${dep}-*.md" | sort | head -n 1)"
    if [[ -z "$dep_file" ]]; then
      unmet+=("${dep}(no-slice-file)")
      continue
    fi
    case "$(ralph_slice_status "$dep_file")" in
      Complete|Superseded) ;;
      *) unmet+=("$dep") ;;
    esac
  done < <(ralph_slice_dependencies "$slice_file")
  if (( ${#unmet[@]} > 0 )); then
    printf '%s\n' "${unmet[@]}"
    return 1
  fi
}

# Print slice paths in execution priority. CR slices can only enter an active
# product backlog through the owner's emergency `ralph-intake.sh --now` path,
# so a grabbable CR must run before ordinary numbered work. Under normal
# maintenance-stage intake there are no unfinished product slices, making the
# same ordering harmless.
ralph_slice_execution_order() {
  local slices_dir="${1:-docs/slices}" file base
  for file in "$slices_dir"/CR-*.md; do
    [[ -f "$file" ]] && printf '%s\n' "$file"
  done
  for file in "$slices_dir"/*.md; do
    [[ -f "$file" ]] || continue
    base="$(basename "$file")"
    [[ "$base" == CR-* ]] && continue
    printf '%s\n' "$file"
  done
}

# Print the basename of the highest-priority grabbable slice. Dependency-
# blocked emergency CRs do not freeze unrelated work: report the blocker and
# continue through the ordinary queue.
ralph_first_grabbable_slice() {
  local slices_dir="${1:-docs/slices}" file unmet
  while IFS= read -r file; do
    [[ -f "$file" ]] || continue
    [[ "$(ralph_slice_status "$file")" == "Not Started" ]] || continue
    if unmet="$(ralph_slice_unmet_dependencies "$file" "$slices_dir")"; then
      basename "$file"
      return 0
    fi
    echo "Skipping $(basename "$file" .md): waiting on $(printf '%s' "$unmet" | tr '\n' ' ' | sed 's/ $//')" >&2
  done < <(ralph_slice_execution_order "$slices_dir")
  return 1
}

# Lint the whole slice queue so newly created slices (architecture-review
# correctives especially) stay executable: every slice has a recognized
# status, every pending slice declares "## Depends On", every reference
# resolves to a real slice file, and the pending graph drains completely
# (no cycles, no permanently stuck chains). Prints one "problem: ..." line
# per finding and returns 1 when any exist. Runs on bash 3.2: membership is
# tracked in newline-delimited strings, not associative arrays.
ralph_slice_queue_lint() {
  local slices_dir="${1:-docs/slices}"
  local problems=0 file base status dep dep_file dep_matches dep_count resolved
  local drained=$'\n' pending=""
  for file in "$slices_dir"/*.md; do
    [[ -f "$file" ]] || continue
    base="$(basename "$file" .md)"
    status="$(ralph_slice_status "$file")"
    case "$status" in
      Complete|Superseded)
        drained="${drained}${base}"$'\n'
        ;;
      "Not Started"|Blocked)
        if ! grep -q '^## Depends On' "$file"; then
          echo "problem: $base has no '## Depends On' section (declare '- None' when it has no blockers)"
          problems=$((problems + 1))
        fi
        resolved=""
        while IFS= read -r dep; do
          [[ -n "$dep" ]] || continue
          dep_matches="$(find "$slices_dir" -maxdepth 1 -type f -name "${dep}-*.md" | sort)"
          dep_count="$(printf '%s\n' "$dep_matches" | grep -c . || true)"
          if (( dep_count == 0 )); then
            echo "problem: $base depends on '$dep' but no ${dep}-*.md slice file exists"
            problems=$((problems + 1))
            continue
          fi
          if (( dep_count > 1 )); then
            echo "problem: $base dependency '$dep' is ambiguous — it matches $dep_count slice files"
            problems=$((problems + 1))
          fi
          dep_file="$(printf '%s\n' "$dep_matches" | head -n 1)"
          resolved="$resolved $(basename "$dep_file" .md)"
        done < <(ralph_slice_dependencies "$file")
        pending="${pending}${base}|${resolved# }"$'\n'
        ;;
      *)
        echo "problem: $base has unrecognized status '$status' (expected Not Started, Blocked, Complete, or Superseded)"
        problems=$((problems + 1))
        ;;
    esac
  done
  local changed=1 line rest dep_base ok remaining
  while (( changed )); do
    changed=0
    remaining=""
    while IFS= read -r line; do
      [[ -n "$line" ]] || continue
      base="${line%%|*}"
      rest="${line#*|}"
      ok=1
      for dep_base in $rest; do
        case "$drained" in
          *$'\n'"$dep_base"$'\n'*) ;;
          *) ok=0; break ;;
        esac
      done
      if (( ok )); then
        drained="${drained}${base}"$'\n'
        changed=1
      else
        remaining="${remaining}${line}"$'\n'
      fi
    done <<< "$pending"
    pending="$remaining"
  done
  if [[ -n "${pending//$'\n'/}" ]]; then
    while IFS= read -r line; do
      [[ -n "$line" ]] || continue
      echo "problem: ${line%%|*} can never become eligible (dependency cycle or stuck chain via: ${line#*|})"
      problems=$((problems + 1))
    done <<< "$pending"
  fi
  (( problems == 0 ))
}

# Print the basenames of every `Not Started` slice, in queue order.
ralph_pending_slices() {
  local slices_dir="${1:-docs/slices}" file
  for file in "$slices_dir"/*.md; do
    [[ -f "$file" ]] || continue
    [[ "$(ralph_slice_status "$file")" == "Not Started" ]] && basename "$file"
  done
  return 0
}

# Print every slice that still represents queued work — `Not Started` or
# `Blocked` — as "basename (status)", in queue order. A queue whose only
# remaining slices are Blocked is unfinished work, not a completed queue.
ralph_remaining_slices() {
  local slices_dir="${1:-docs/slices}" file status
  for file in "$slices_dir"/*.md; do
    [[ -f "$file" ]] || continue
    status="$(ralph_slice_status "$file")"
    case "$status" in
      "Not Started"|Blocked) echo "$(basename "$file" .md) ($status)" ;;
    esac
  done
  return 0
}

# Decide whether one slice-status transition observed in a run's diff is
# allowed. Args: mode, selected slice basename, changed slice basename,
# old status, new status. Implementation agents never own status transitions;
# the orchestrator marks the selected slice Complete only after validation.
# Architecture reviews may re-park other slices but cannot alter their own
# pseudo-slice or mark any product slice Complete.
ralph_slice_transition_allowed() {
  local mode="${1:?mode is required}" selected="${2:?selected slice is required}"
  local base="${3:?slice basename is required}" old="$4" new="$5"
  [[ "$old" == "$new" ]] && return 0
  [[ "$base" == "$selected" ]] && return 1
  if [[ "$mode" == "architecture_review" ]]; then
    [[ "$new" == "Complete" ]] && return 1
    return 0
  fi
  return 1
}
