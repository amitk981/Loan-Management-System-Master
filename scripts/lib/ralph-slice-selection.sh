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

# Print the basenames of every `Not Started` slice, in queue order.
ralph_pending_slices() {
  local slices_dir="${1:-docs/slices}" file
  for file in "$slices_dir"/*.md; do
    [[ -f "$file" ]] || continue
    [[ "$(ralph_slice_status "$file")" == "Not Started" ]] && basename "$file"
  done
  return 0
}
