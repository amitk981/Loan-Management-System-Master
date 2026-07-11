#!/usr/bin/env bash

# Slice files follow the to-issues standard: each declares its blockers under
# "## Depends On", and a slice is grabbable only when every blocker is done.
# Selection therefore walks the sorted queue and takes the first `Not Started`
# slice whose declared dependencies are all Complete or Superseded.

ralph_slice_status() {
  awk '/^## Status/ { getline; print; exit }' "${1:?slice file is required}"
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

# Lint the whole slice queue so newly created slices (architecture-review
# correctives especially) stay executable: every slice has a recognized
# status, every pending slice declares "## Depends On", every reference
# resolves to a real slice file, and the pending graph drains completely
# (no cycles, no permanently stuck chains). Prints one "problem: ..." line
# per finding and returns 1 when any exist. Runs on bash 3.2: membership is
# tracked in newline-delimited strings, not associative arrays.
ralph_slice_queue_lint() {
  local slices_dir="${1:-docs/slices}"
  local problems=0 file base status dep dep_file resolved
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
          dep_file="$(find "$slices_dir" -maxdepth 1 -type f -name "${dep}-*.md" | sort | head -n 1)"
          if [[ -z "$dep_file" ]]; then
            echo "problem: $base depends on '$dep' but no ${dep}-*.md slice file exists"
            problems=$((problems + 1))
            continue
          fi
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
