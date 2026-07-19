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
  local screenshot_count=0
  local seen_specs=""
  local seen_screenshots=""
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
        elif printf '%s\n' "$seen_specs" | grep -Fxq "$value"; then
          echo "Duplicate trusted browser spec '$value' in $slice_file." >&2
          problem_count=$((problem_count + 1))
        else
          spec_count=$((spec_count + 1))
          seen_specs="${seen_specs}${seen_specs:+$'\n'}${value}"
        fi
        ;;
      "Screenshot: "*)
        value="${entry#Screenshot: }"
        if [[ ! "$value" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*\.png$ ]]; then
          echo "Invalid trusted browser screenshot '$value' in $slice_file; use a PNG basename only." >&2
          problem_count=$((problem_count + 1))
        elif printf '%s\n' "$seen_screenshots" | grep -Fxq "$value"; then
          echo "Duplicate trusted browser screenshot '$value' in $slice_file." >&2
          problem_count=$((problem_count + 1))
        else
          screenshot_count=$((screenshot_count + 1))
          seen_screenshots="${seen_screenshots}${seen_screenshots:+$'\n'}${value}"
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
  if (( screenshot_count == 0 )); then
    echo "Slice $slice_file declares localhost-e2e-server but no valid trusted browser Screenshot entry." >&2
    problem_count=$((problem_count + 1))
  fi

  (( problem_count == 0 ))
}

ralph_write_trusted_browser_screenshot_manifest() {
  local slice_file="${1:?slice file is required}"
  local evidence_dir="${2:?browser evidence directory is required}"
  local manifest_file="${3:?screenshot manifest path is required}"
  local screenshot=""
  local screenshot_path=""
  local signature=""
  local hash=""
  local screenshot_count=0
  local problem_count=0
  local manifest_tmp="${manifest_file}.tmp.$$"

  mkdir -p "$(dirname "$manifest_file")"
  : > "$manifest_tmp"

  while IFS= read -r screenshot; do
    [[ -n "$screenshot" ]] || continue
    screenshot_count=$((screenshot_count + 1))
    screenshot_path="$evidence_dir/$screenshot"
    if [[ -L "$screenshot_path" || ! -f "$screenshot_path" || ! -s "$screenshot_path" ]]; then
      echo "Missing, empty, or symlinked trusted browser screenshot for this run: $screenshot_path" >&2
      problem_count=$((problem_count + 1))
      continue
    fi
    signature="$(od -An -t x1 -N 8 "$screenshot_path" 2>/dev/null | tr -d '[:space:]')"
    if [[ "$signature" != "89504e470d0a1a0a" ]]; then
      echo "Trusted browser evidence is not a PNG file: $screenshot_path" >&2
      problem_count=$((problem_count + 1))
      continue
    fi
    if command -v shasum >/dev/null 2>&1; then
      hash="$(shasum -a 256 "$screenshot_path" | awk '{print $1}')"
    elif command -v sha256sum >/dev/null 2>&1; then
      hash="$(sha256sum "$screenshot_path" | awk '{print $1}')"
    else
      echo "Neither shasum nor sha256sum is available for screenshot evidence." >&2
      problem_count=$((problem_count + 1))
      continue
    fi
    printf '%s  %s\n' "$hash" "$screenshot" >> "$manifest_tmp"
  done < <(ralph_trusted_e2e_screenshots "$slice_file")

  if (( screenshot_count == 0 )); then
    echo "No trusted browser screenshots were declared for $slice_file." >&2
    problem_count=$((problem_count + 1))
  fi
  if (( problem_count > 0 )); then
    rm -f "$manifest_tmp"
    return 1
  fi
  mv "$manifest_tmp" "$manifest_file"
}
