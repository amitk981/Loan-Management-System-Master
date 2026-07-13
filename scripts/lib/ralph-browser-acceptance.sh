#!/usr/bin/env bash

ralph_trusted_browser_acceptance_entries() {
  local slice_file="${1:?slice file is required}"

  awk '
    $0 == "## Trusted Browser Acceptance" { in_acceptance = 1; next }
    in_acceptance && /^## / { exit }
    in_acceptance {
      line = $0
      sub(/^[[:space:]]*-[[:space:]]*/, "", line)
      gsub(/`/, "", line)
      sub(/^[[:space:]]+/, "", line)
      sub(/[[:space:]]+$/, "", line)
      if (length(line) > 0) print line
    }
  ' "$slice_file"
}

ralph_trusted_e2e_specs() {
  local slice_file="${1:?slice file is required}"
  local entry=""

  while IFS= read -r entry; do
    case "$entry" in
      "Spec: "*) printf '%s\n' "${entry#Spec: }" ;;
    esac
  done < <(ralph_trusted_browser_acceptance_entries "$slice_file")
}

ralph_trusted_e2e_screenshots() {
  local slice_file="${1:?slice file is required}"
  local entry=""

  while IFS= read -r entry; do
    case "$entry" in
      "Screenshot: "*) printf '%s\n' "${entry#Screenshot: }" ;;
    esac
  done < <(ralph_trusted_browser_acceptance_entries "$slice_file")
}

ralph_validate_trusted_browser_acceptance() {
  local slice_file="${1:?slice file is required}"
  local project_dir="${2:?project directory is required}"
  local entry=""
  local value=""
  local spec_count=0
  local problem_count=0

  while IFS= read -r entry; do
    case "$entry" in
      "Spec: "*)
        value="${entry#Spec: }"
        if [[ ! "$value" =~ ^e2e/[A-Za-z0-9._/-]+\.spec\.ts$ \
              || "$value" == *".."* \
              || "$value" == *"//"* ]]; then
          echo "Invalid trusted browser spec path '$value' in $slice_file; use a relative e2e/*.spec.ts path." >&2
          problem_count=$((problem_count + 1))
        elif [[ ! -f "$project_dir/$value" ]]; then
          echo "Trusted browser spec '$value' does not exist under $project_dir." >&2
          problem_count=$((problem_count + 1))
        else
          spec_count=$((spec_count + 1))
        fi
        ;;
      "Screenshot: "*)
        value="${entry#Screenshot: }"
        if [[ ! "$value" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*\.png$ ]]; then
          echo "Invalid trusted browser screenshot '$value' in $slice_file; use a PNG basename only." >&2
          problem_count=$((problem_count + 1))
        fi
        ;;
      *)
        echo "Unknown trusted browser acceptance entry '$entry' in $slice_file." >&2
        problem_count=$((problem_count + 1))
        ;;
    esac
  done < <(ralph_trusted_browser_acceptance_entries "$slice_file")

  if (( spec_count == 0 )); then
    echo "Slice $slice_file declares localhost-e2e-server but no valid trusted browser Spec entry." >&2
    problem_count=$((problem_count + 1))
  fi

  (( problem_count == 0 ))
}
