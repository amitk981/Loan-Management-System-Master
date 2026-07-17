#!/usr/bin/env bash
# Change-request intake gate (maintenance stage).
# Validates docs/change-requests/inbox/*.md against the strict template.
# Invalid file  -> precise errors, nothing promoted, no code will change.
# Valid file    -> converted to a CR-NNN slice in docs/slices/ (original
#                  archived to docs/change-requests/accepted/), where the
#                  normal Ralph pipeline picks it up with all gates plus
#                  the mandatory impact-analysis gate.
# Refuses to run while unfinished product slices remain, unless --now.
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root"

if [[ "$repo_root" == *"/.ralph/worktrees/"* ]]; then
  echo "Refusing to run: current directory is inside a Ralph worktree." >&2
  exit 1
fi

allow_now=0
[[ "${1:-}" == "--now" ]] && allow_now=1

inbox="docs/change-requests/inbox"
accepted="docs/change-requests/accepted"
mkdir -p "$inbox" "$accepted"

# Stage gate: the product backlog must be finished first.
if (( allow_now == 0 )); then
  unfinished_count=0
  for f in docs/slices/*.md; do
    base="$(basename "$f")"
    [[ "$base" == CR-* ]] && continue
    status="$(awk '/^## Status/ { getline; print; exit }' "$f" | xargs || true)"
    [[ "$status" == "Not Started" ]] && unfinished_count=$((unfinished_count + 1))
  done
  if (( unfinished_count > 0 )); then
    echo "Intake refused: $unfinished_count product slice(s) are still Not Started." >&2
    echo "Change requests open in the maintenance stage, after the backlog is finished." >&2
    echo "Owner emergency override: ./scripts/ralph-intake.sh --now" >&2
    exit 2
  fi
fi

required_sections=("Type" "Severity" "Expected Behaviour" "Where It Appears" "Source Document Reference" "Acceptance Criteria")
valid_types="bug-frontend bug-backend bug-cross-stack ui-change feature"

section_body() {
  # Print the body of "## $2" in file $1 (lines until the next heading).
  awk -v h="## $2" '
    $0 == h { grab = 1; next }
    grab && /^## / { exit }
    grab { print }
  ' "$1"
}

promoted=0
rejected=0
shopt -s nullglob
for cr in "$inbox"/*.md; do
  base="$(basename "$cr")"
  [[ "$base" == TEMPLATE-* ]] && continue

  errors=()

  title="$(awk '/^# / { sub(/^# /, ""); print; exit }' "$cr")"
  [[ -z "$title" || "$title" == \<* ]] && errors+=("Missing or unfilled title line ('# <short title>').")

  for section in "${required_sections[@]}"; do
    body="$(section_body "$cr" "$section" | grep -v '^[[:space:]]*$' || true)"
    if [[ -z "$body" ]]; then
      errors+=("Section '## $section' is missing or empty.")
    elif [[ "$body" == \<* ]]; then
      errors+=("Section '## $section' still contains template placeholder text.")
    fi
  done

  cr_type="$(section_body "$cr" "Type" | grep -v '^[[:space:]]*$' | head -1 | xargs || true)"
  if [[ -n "$cr_type" && " $valid_types " != *" $cr_type "* ]]; then
    errors+=("Type '$cr_type' is not one of: $valid_types.")
  fi

  if [[ "$cr_type" == "feature" || "$cr_type" == "ui-change" ]]; then
    wr="$(section_body "$cr" "What Is Requested" | grep -v '^[[:space:]]*$' || true)"
    { [[ -z "$wr" || "$wr" == \<* ]]; } && errors+=("'$cr_type' requests need a filled '## What Is Requested' section.")
  elif [[ "$cr_type" == bug-* ]]; then
    wh="$(section_body "$cr" "What Is Happening" | grep -v '^[[:space:]]*$' || true)"
    st="$(section_body "$cr" "Steps To Reproduce" | grep -v '^[[:space:]]*$' || true)"
    { [[ -z "$wh" || "$wh" == \<* ]]; } && errors+=("Bug reports need a filled '## What Is Happening' section.")
    { [[ -z "$st" || "$st" == \<* ]]; } && errors+=("Bug reports need a filled '## Steps To Reproduce' section.")
  fi

  # A ui-change deviates from the approved prototype design, so it must be
  # explicitly owner-approved — otherwise FRONTEND_DESIGN_RULES forbids it.
  if [[ "$cr_type" == "ui-change" ]]; then
    sdr="$(section_body "$cr" "Source Document Reference" || true)"
    if ! printf '%s' "$sdr" | grep -qi "owner approved"; then
      errors+=("ui-change requests must contain the phrase 'owner approved' in '## Source Document Reference' — a UI change amends the approved design and needs your explicit sign-off in the file.")
    fi
  fi

  if (( ${#errors[@]} > 0 )); then
    rejected=$((rejected + 1))
    echo "REJECTED: $base — nothing was changed for this request."
    for e in "${errors[@]}"; do echo "  - $e"; done
    continue
  fi

  # Promote: next CR number.
  last=0
  for existing in docs/slices/CR-*.md; do
    n="$(basename "$existing" | sed -E 's/^CR-([0-9]+).*/\1/')"
    if [[ "$n" =~ ^[0-9]+$ ]]; then
      decimal_n=$((10#$n))
      (( decimal_n > last )) && last=$decimal_n
    fi
  done
  next=$(printf 'CR-%03d' $((last + 1)))

  slug="$(basename "$cr" .md | tr '[:upper:] ' '[:lower:]-' | tr -cd 'a-z0-9-')"
  slice_file="docs/slices/${next}-${slug}.md"

  severity="$(section_body "$cr" "Severity" | grep -v '^[[:space:]]*$' | head -1 | xargs || true)"
  risk="Medium"
  [[ "$severity" == "Critical" || "$severity" == "High" || "$cr_type" == "feature" || "$cr_type" == "bug-cross-stack" || "$cr_type" == "ui-change" ]] && risk="High"

  {
    echo "# Slice ${next}: ${title}"
    echo
    echo "## Status"
    echo "Not Started"
    echo
    echo "## Origin"
    echo "Change request (maintenance stage), accepted $(date '+%Y-%m-%d') from docs/change-requests/accepted/${next}-${base}."
    echo
    echo "## Risk Level"
    echo "$risk"
    echo
    echo "## Change Request (verbatim)"
    echo
    cat "$cr"
    echo
    echo "## Mandatory First Step: Impact Analysis"
    echo "Before changing ANY code, write impact-analysis.md in the run folder covering:"
    echo "- Affected backend models/endpoints/services, with grep evidence."
    echo "- Affected frontend screens/components/routes."
    echo "- Blast radius: every OTHER module that consumes the affected pieces."
    echo "- Existing tests covering the affected pieces, and the regression tests to add in EACH affected module."
    echo "- FRONTEND_DESIGN_RULES compliance note for any UI change."
    echo "Validation fails this run if impact-analysis.md is missing."
    echo
    echo "## Acceptance Criteria"
    echo "- The change request's own acceptance criteria are met."
    echo "- Regression tests added for every module named in the impact analysis."
    echo "- All quality gates pass."
  } > "$slice_file"

  mv "$cr" "$accepted/${next}-${base}"
  promoted=$((promoted + 1))
  echo "ACCEPTED: $base -> $slice_file (risk: $risk)"
done

echo
echo "Intake finished: $promoted promoted, $rejected rejected."
(( rejected > 0 )) && exit 1
exit 0
