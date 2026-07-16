#!/usr/bin/env bash

# Run every deterministic candidate blocker before browser, frontend,
# PostgreSQL, or backend gates consume meaningful time. This function is the
# authoritative implementation for these checks and writes the same detailed
# evidence files consumed by repair mode.
ralph_run_fast_candidate_checks() {
  local worktree_dir="${1:?worktree directory is required}"
  local run_dir="${2:?run directory is required}"
  local config="${3:?config path is required}"
  local mode="${4:?mode is required}"
  local slice_id="${5:-}"
  local postgres_acceptance_required="${6:-0}"
  local report="$run_dir/candidate-fast-check-results.md"
  local failures=0
  local changed_paths changed protected protected_violations=0
  local queue_lint_problems lint_line
  local st_path st_old st_new st_base st_violations=0 st_checked=0
  local max_files max_lines files_changed tracked_lines untracked_lines total_lines f
  local review_packet declared_result declared_result_normalized declared_result_is_failure=0
  local impact_file ia_results noop_file agent_changes aq_file dl_file artifact_file declared_file required

  changed_paths="$( (cd "$worktree_dir" && git status --porcelain) \
    | sed -E 's/^.{3}//; s/.* -> //; s/^"//; s/"$//' )"

  local guard_file="$run_dir/protected-paths-check.md"
  {
    echo "# Protected Paths Check"
    echo
  } > "$guard_file"
  local protected_paths=(
    "scripts/"
    ".github/"
    ".ralph/config.yaml"
    ".ralph/permissions.json"
    ".codex/config.toml"
    "AGENTS.md"
    "CLAUDE.md"
    ".gitignore"
    "docs/working/HIGH_RISK_APPROVALS.md"
    "docs/working/DECISION_POLICY.md"
    "docs/working/FRONTEND_DESIGN_RULES.md"
    "docs/change-requests/TEMPLATE-bug.md"
    "docs/change-requests/TEMPLATE-feature.md"
    "docs/change-requests/TEMPLATE-slice.md"
    "docs/change-requests/TEMPLATE-epic.md"
    "docs/change-requests/README.md"
    "docs/source/"
  )
  while IFS= read -r changed; do
    [[ -n "$changed" ]] || continue
    for protected in "${protected_paths[@]}"; do
      if [[ "$changed" == "$protected" || "$changed" == "$protected"* ]]; then
        echo "- FAIL: protected path modified by this run: $changed" >> "$guard_file"
        protected_violations=$((protected_violations + 1))
      fi
    done
  done <<< "$changed_paths"
  if (( protected_violations > 0 )); then
    echo >> "$guard_file"
    echo "Protected files may only be changed by the human owner outside Ralph runs." >> "$guard_file"
    failures=$((failures + protected_violations))
  else
    echo "- PASS: no protected paths were modified." >> "$guard_file"
  fi

  local queue_lint_file="$run_dir/slice-queue-lint.md"
  {
    echo "# Slice Queue Lint"
    echo
  } > "$queue_lint_file"
  queue_lint_problems="$(ralph_slice_queue_lint "$worktree_dir/docs/slices" || true)"
  if [[ -n "$queue_lint_problems" ]]; then
    while IFS= read -r lint_line; do
      [[ -n "$lint_line" ]] && echo "- FAIL: ${lint_line#problem: }" >> "$queue_lint_file"
    done <<< "$queue_lint_problems"
    echo >> "$queue_lint_file"
    echo "New or edited slices must retain a parseable, drainable dependency graph." >> "$queue_lint_file"
    failures=$((failures + 1))
  else
    echo "- PASS: every slice parses and the pending Depends On graph drains completely." >> "$queue_lint_file"
  fi

  local st_file="$run_dir/slice-status-transition-check.md"
  {
    echo "# Slice Status Transition Check"
    echo
  } > "$st_file"
  while IFS= read -r st_path; do
    case "$st_path" in
      docs/slices/*.md) ;;
      *) continue ;;
    esac
    st_old="$( (cd "$worktree_dir" && git show "HEAD:$st_path" 2>/dev/null || true) | awk '/^## Status/ { getline; print; exit }' )"
    [[ -n "$st_old" ]] || continue
    if [[ -f "$worktree_dir/$st_path" ]]; then
      st_new="$(ralph_slice_status "$worktree_dir/$st_path")"
    else
      st_new="(deleted)"
    fi
    st_base="$(basename "$st_path" .md)"
    st_checked=$((st_checked + 1))
    if ralph_slice_transition_allowed "$mode" "${slice_id:-}" "$st_base" "$st_old" "$st_new"; then
      if [[ "$st_old" != "$st_new" ]]; then
        echo "- PASS: $st_base status '$st_old' -> '$st_new' (allowed for this run)." >> "$st_file"
      fi
    else
      echo "- FAIL: $st_base status changed '$st_old' -> '$st_new' but this run executed '${slice_id:-<none>}'." >> "$st_file"
      st_violations=$((st_violations + 1))
    fi
  done <<< "$changed_paths"
  if (( st_violations > 0 )); then
    echo >> "$st_file"
    echo "A run may only transition the slice it executed; reviews may re-park other slices but never mark them Complete." >> "$st_file"
    failures=$((failures + st_violations))
  elif (( st_checked == 0 )); then
    echo "- PASS: no existing slice files were modified." >> "$st_file"
  else
    echo "- PASS: all slice status transitions are allowed for this run." >> "$st_file"
  fi

  if [[ "$mode" == "normal_run" && "$slice_id" == CR-* ]]; then
    impact_file="$run_dir/impact-analysis.md"
    ia_results="$run_dir/impact-analysis-check-results.md"
    if [[ -s "$impact_file" ]] && grep -qi "blast radius\|affected" "$impact_file" && grep -qi "regression" "$impact_file"; then
      printf '# Impact Analysis Check Results\n\nPASS: impact-analysis.md exists and covers affected modules and regression tests.\n' > "$ia_results"
    else
      {
        echo "# Impact Analysis Check Results"
        echo
        echo "FAIL: change-request slice $slice_id requires impact-analysis.md in the run folder,"
        echo "covering affected modules (blast radius) and the regression tests to add per module."
      } > "$ia_results"
      failures=$((failures + 1))
    fi
  fi

  if [[ "$mode" == "normal_run" ]]; then
    noop_file="$run_dir/no-op-check-results.md"
    agent_changes="$(printf '%s\n' "$changed_paths" | grep -v '^\.ralph/' | grep -v '^$' || true)"
    if [[ -z "$agent_changes" ]]; then
      if [[ "$slice_id" == "006F4-postgresql-credit-concurrency-acceptance" && "$postgres_acceptance_required" == "1" ]]; then
        {
          echo "# No-Op Check Results"
          echo
          echo "PASS: acceptance-only slice is eligible for its authoritative PostgreSQL gate."
          echo "The candidate still fails unless that required gate passes."
        } > "$noop_file"
      else
        {
          echo "# No-Op Check Results"
          echo
          echo "FAIL: the agent produced no changes outside .ralph/ bookkeeping."
          echo "A normal run cannot complete a slice with zero product/doc changes."
        } > "$noop_file"
        failures=$((failures + 1))
      fi
    else
      {
        echo "# No-Op Check Results"
        echo
        echo "PASS: the run produced real changes:"
        printf '%s\n' "$agent_changes" | sed 's/^/- /'
      } > "$noop_file"
    fi
  fi

  aq_file="$run_dir/artifact-quality-check.md"
  printf '# Artifact Quality Check\n\n' > "$aq_file"
  if grep -qF "must replace this template" "$run_dir/execution-plan.md" 2>/dev/null \
      && ! grep -Eq '^[[:space:]]*[0-9]+\.[[:space:]]+' "$run_dir/execution-plan.md" 2>/dev/null; then
    echo "- FAIL: execution-plan.md is still the unfilled template." >> "$aq_file"
    failures=$((failures + 1))
  else
    echo "- PASS: execution-plan.md was filled in." >> "$aq_file"
  fi
  if grep -qF "To be completed by the selected agent" "$run_dir/risk-assessment.md" 2>/dev/null; then
    echo "- FAIL: risk-assessment.md is still the unfilled template." >> "$aq_file"
    failures=$((failures + 1))
  else
    echo "- PASS: risk-assessment.md was filled in." >> "$aq_file"
  fi

  if [[ "$mode" =~ ^(normal_run|repair)$ ]]; then
    max_files="$(awk -F': *' '/^[[:space:]]*max_changed_files:/ {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' "$config" | xargs || true)"
    max_lines="$(awk -F': *' '/^[[:space:]]*max_lines_changed:/ {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' "$config" | xargs || true)"
    max_files="${max_files:-30}"
    max_lines="${max_lines:-2000}"
    files_changed="$(printf '%s\n' "$changed_paths" | grep -v '^\.ralph/' | grep -cv '^$' || true)"
    tracked_lines="$( (cd "$worktree_dir" && git diff --numstat HEAD -- . ':(exclude).ralph') \
      | awk '{added=$1; deleted=$2; if (added != "-") total += added; if (deleted != "-") total += deleted} END {print total + 0}')"
    untracked_lines=0
    while IFS= read -r f; do
      [[ -z "$f" || ! -f "$worktree_dir/$f" ]] && continue
      untracked_lines=$((untracked_lines + $(wc -l < "$worktree_dir/$f" 2>/dev/null || echo 0)))
    done < <( (cd "$worktree_dir" && git ls-files --others --exclude-standard) | grep -v '^\.ralph/' || true)
    total_lines=$((tracked_lines + untracked_lines))
    dl_file="$run_dir/diff-limits-results.md"
    {
      echo "# Diff Limits Results"
      echo
      echo "- Files changed (excluding .ralph/): $files_changed (limit $max_files)"
      echo "- Lines changed (tracked + new files, excluding .ralph/): $total_lines (limit $max_lines)"
    } > "$dl_file"
    if (( files_changed > max_files )); then
      echo "- FAIL: changed-file count exceeds limits.max_changed_files." >> "$dl_file"
      failures=$((failures + 1))
    fi
    if (( total_lines > max_lines )); then
      echo "- FAIL: changed-line count exceeds limits.max_lines_changed." >> "$dl_file"
      failures=$((failures + 1))
    fi
    if (( files_changed <= max_files && total_lines <= max_lines )); then
      echo "- PASS: within diff limits." >> "$dl_file"
    fi
  fi

  artifact_file="$run_dir/ralph-artifact-validation.md"
  {
    echo "# Ralph Artifact Validation"
    echo
    echo "- Run folder: $run_dir"
  } > "$artifact_file"
  for required in prompt.md execution-plan.md changed-files.txt risk-assessment.md final-summary.md review-packet.md; do
    if [[ -f "$run_dir/$required" ]]; then
      echo "- PASS: $required exists." >> "$artifact_file"
    else
      echo "- FAIL: $required is missing." >> "$artifact_file"
      failures=$((failures + 1))
    fi
  done
  if python3 -m json.tool "$worktree_dir/.ralph/state.json" >/dev/null; then
    echo "- PASS: state.json is valid." >> "$artifact_file"
  else
    echo "- FAIL: state.json invalid." >> "$artifact_file"
    failures=$((failures + 1))
  fi
  if python3 -m json.tool "$worktree_dir/.ralph/permissions.json" >/dev/null; then
    echo "- PASS: permissions.json is valid." >> "$artifact_file"
  else
    echo "- FAIL: permissions.json invalid." >> "$artifact_file"
    failures=$((failures + 1))
  fi
  if command -v ruby >/dev/null 2>&1; then
    if ruby -e 'require "yaml"; YAML.load_file(ARGV[0])' "$config" >/dev/null 2>&1; then
      echo "- PASS: config.yaml is parseable." >> "$artifact_file"
    else
      echo "- FAIL: config.yaml invalid." >> "$artifact_file"
      failures=$((failures + 1))
    fi
  fi

  declared_file="$run_dir/agent-declared-result-check.md"
  printf '# Agent-Declared Result Check\n\n' > "$declared_file"
  review_packet="$run_dir/review-packet.md"
  if [[ "$mode" != "normal_run" && "$mode" != "repair" ]]; then
    echo "- SKIP: mode $mode (architecture-review packets may quote failure phrases from findings)." >> "$declared_file"
  elif [[ -f "$review_packet" ]]; then
    declared_result="$(awk '/^## Result/{while ((getline line) > 0) { if (line !~ /^[[:space:]]*$/) { print line; exit } }}' "$review_packet" | xargs || true)"
    declared_result_normalized="$(printf '%s' "$declared_result" | tr '[:upper:]' '[:lower:]')"
    case "$declared_result_normalized" in
      fail|fail\ *|failed|failed\ *|blocked|blocked\ *) declared_result_is_failure=1 ;;
    esac
    if (( declared_result_is_failure == 1 )) || grep -qiE 'do not (commit|merge)' "$review_packet"; then
      echo "- FAIL: the agent's review-packet.md declares this run failed or unmergeable (Result: ${declared_result:-<none>})." >> "$declared_file"
      failures=$((failures + 1))
    else
      echo "- PASS: review-packet.md declares no failed/blocked/unmergeable result (Result: ${declared_result:-In Progress})." >> "$declared_file"
    fi
  else
    echo "- FAIL: review-packet.md is missing." >> "$declared_file"
    failures=$((failures + 1))
  fi

  {
    echo "# Candidate Fast Check Results"
    echo
    echo "Checks ran before all expensive validation lanes."
    echo
    if (( failures > 0 )); then
      grep -H -E '(^|- )FAIL' "$guard_file" "$queue_lint_file" "$st_file" "$aq_file" \
        "$artifact_file" "$declared_file" "$run_dir"/*-results.md 2>/dev/null \
        | sed "s|$run_dir/||" | head -60 || true
    else
      echo "PASS: candidate is eligible for expensive validation gates."
    fi
  } > "$report"

  RALPH_FAST_CANDIDATE_FAILURES="$failures"
  if (( failures > 0 )); then
    {
      echo "# Failure Summary"
      echo
      echo "Cheap candidate validation failed before expensive gates."
      echo
      sed -n '/FAIL/p' "$report"
    } > "$run_dir/failure-summary.md"
    return 1
  fi
  return 0
}
