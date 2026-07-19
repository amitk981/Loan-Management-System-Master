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

# Return the review decision the loop should enforce without rewriting durable
# state. A boundary reason is temporarily deferred while explicit same-epic
# work remains; cadence, failed-review, completion, malformed, and mixed reasons
# remain fail-closed. Keeping the durable due flag preserves the targeted cycle
# until the terminal corrective actually completes.
ralph_architecture_review_effective_due() {
  local state_file="${1:?state file is required}" slice_dir="${2:?slice directory is required}"
  local due reason part epic kept=0 deferred=0
  local boundary_pattern='^epic_boundary:([0-9][0-9][0-9])->'
  due="$(ralph_architecture_review_due "$state_file")" || return 1
  if [[ "$due" != "True" ]]; then
    printf 'False\n'
    return 0
  fi
  reason="$(python3 - "$state_file" <<'PY'
import json, sys
print(json.load(open(sys.argv[1])).get("architecture_review_due_reason", ""))
PY
)"
  if [[ -z "$reason" ]]; then
    printf 'True\n'
    return 0
  fi
  IFS='+' read -r -a parts <<< "$reason"
  for part in "${parts[@]}"; do
    if [[ "$part" =~ $boundary_pattern ]]; then
      epic="${BASH_REMATCH[1]}"
      if ralph_queue_has_unfinished_parent_epic "$slice_dir" "$epic"; then
        deferred=1
        continue
      fi
    fi
    kept=1
  done
  if (( kept == 1 || deferred == 0 )); then
    printf 'True\n'
  else
    printf 'False\n'
  fi
}

# Retained for the startup diagnostic interface. Reconciliation is deliberately
# read-only: mutating tracked state here makes clean-tree preflight reject the
# orchestrator's own change before a candidate worktree exists.
ralph_reconcile_architecture_review_due() {
  local state_file="${1:?state file is required}" slice_dir="${2:?slice directory is required}"
  local durable effective reason epic
  local boundary_pattern='^epic_boundary:([0-9][0-9][0-9])->'
  durable="$(ralph_architecture_review_due "$state_file")" || return 1
  effective="$(ralph_architecture_review_effective_due "$state_file" "$slice_dir")" || return 1
  if [[ "$durable" == "True" && "$effective" == "False" ]]; then
    reason="$(python3 - "$state_file" <<'PY'
import json, sys
print(json.load(open(sys.argv[1])).get("architecture_review_due_reason", ""))
PY
)"
    IFS='+' read -r -a parts <<< "$reason"
    for part in "${parts[@]}"; do
      if [[ "$part" =~ $boundary_pattern ]]; then
        epic="${BASH_REMATCH[1]}"
        if ralph_queue_has_unfinished_parent_epic "$slice_dir" "$epic"; then
          printf 'Deferred premature architecture-review boundary for Epic %s; same-epic work remains.\n' \
            "$epic"
          return 0
        fi
      fi
    done
  fi
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

# Validate the narrow owner-controlled exit for an exhausted corrective cycle.
# A slice declaration is insufficient: the protected approvals file must name
# the exact CR, epic, and generation, and durable state must prove the configured
# corrective-generation cap has actually been reached.
ralph_architecture_review_finalizer_epic() {
  local config="${1:?config is required}" state_file="${2:?state file is required}"
  local slice_file="${3:?slice file is required}" approvals_file="${4:?approvals file is required}"
  local base slice_id approval_id fields epic generation maximum state_values
  local due cycle state_generation reason risk parent reason_pattern
  [[ -f "$slice_file" && -f "$approvals_file" ]] || return 1
  base="$(basename "$slice_file")"
  [[ "$base" =~ ^(CR-[0-9][0-9][0-9][0-9]*)-.+\.md$ ]] || return 1
  approval_id="${BASH_REMATCH[1]}"
  slice_id="${base%.md}"
  [[ "$(awk '/^## Status[[:space:]]*$/ {getline; print; exit}' "$slice_file")" == "Not Started" ]] \
    || return 1
  risk="$(awk '/^## Risk Level[[:space:]]*$/ {getline; print; exit}' "$slice_file" | xargs || true)"
  [[ "$risk" == "High" ]] || return 1
  fields="$(awk '
    /^## Architecture Review Finalizer[[:space:]]*$/ {
      sections += 1
      inside = (sections == 1)
      next
    }
    inside && /^## / { inside = 0 }
    inside && /^- Epic: / {
      epic_count += 1
      epic = $0
      sub(/^- Epic: /, "", epic)
      next
    }
    inside && /^- Exhausted corrective generation: / {
      generation_count += 1
      generation = $0
      sub(/^- Exhausted corrective generation: /, "", generation)
      next
    }
    inside && /[^[:space:]]/ { unknown += 1 }
    END {
      if (sections == 1 && epic_count == 1 && generation_count == 1 && unknown == 0) {
        print epic "\t" generation
      }
    }
  ' "$slice_file")"
  IFS=$'\t' read -r epic generation <<< "$fields"
  [[ "$epic" =~ ^[0-9][0-9][0-9]$ && "$generation" =~ ^[1-9][0-9]*$ ]] || return 1
  maximum="$(awk -F': *' '/^[[:space:]]*architecture_review_max_corrective_generations:/ {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' "$config" | xargs || true)"
  maximum="${maximum:-2}"
  [[ "$maximum" =~ ^[1-9][0-9]*$ ]] || return 1
  state_values="$(python3 - "$state_file" <<'PY'
import json
import sys

try:
    state = json.load(open(sys.argv[1]))
    due = state.get("architecture_review_due")
    cycle = state.get("architecture_review_cycle_epic", "")
    generation = int(state.get("architecture_review_corrective_generation", 0))
    reason = state.get("architecture_review_due_reason", "")
except (OSError, TypeError, ValueError, json.JSONDecodeError):
    raise SystemExit(1)
if not isinstance(due, bool) or not isinstance(cycle, str) or not isinstance(reason, str):
    raise SystemExit(1)
print(f"{'True' if due else 'False'}\t{cycle}\t{generation}\t{reason}")
PY
)" || return 1
  IFS=$'\t' read -r due cycle state_generation reason <<< "$state_values"
  [[ "$due" == "True" && "$cycle" == "$epic" \
      && "$state_generation" == "$generation" ]] || return 1
  (( generation >= maximum )) || return 1
  reason_pattern="(^|\\+)epic_(boundary:${epic}->[0-9][0-9][0-9]|completion:${epic})(\\+|$)"
  [[ "$reason" =~ $reason_pattern ]] || return 1
  parent="$(ralph_slice_parent_epics "$(dirname "$slice_file")" "$slice_id")"
  printf '%s\n' "$parent" | grep -Fxq "$epic" || return 1
  grep -qF -- \
    "- [approved-finalizer] $approval_id | Epic $epic | generation $generation |" \
    "$approvals_file" || return 1
  printf '%s\n' "$epic"
}

# Apply the trusted post-validation transition. Only the orchestrator calls
# this after every declared product gate passes; candidate content cannot grant
# itself authority to clear an exhausted architecture-review cycle.
ralph_finalize_architecture_review_cycle() {
  local state_file="${1:?state file is required}" epic="${2:?epic is required}"
  local slice_id="${3:?slice id is required}" run_id="${4:?run id is required}"
  [[ "$epic" =~ ^[0-9][0-9][0-9]$ \
      && "$slice_id" =~ ^CR-[0-9][A-Za-z0-9._-]*$ \
      && "$run_id" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]] || return 1
  python3 - "$state_file" "$epic" "$slice_id" "$run_id" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
epic, slice_id, run_id = sys.argv[2:]
state = json.loads(path.read_text())
if state.get("architecture_review_due") is not True:
    raise SystemExit("architecture-review finalizer requires a due review")
if state.get("architecture_review_cycle_epic") != epic:
    raise SystemExit("architecture-review finalizer epic does not match the active cycle")
if int(state.get("architecture_review_corrective_generation", 0)) < 1:
    raise SystemExit("architecture-review finalizer requires a corrective generation")
state["architecture_review_due"] = False
state.pop("architecture_review_due_reason", None)
state.pop("architecture_review_cycle_epic", None)
state.pop("architecture_review_corrective_generation", None)
state["slices_completed_since_architecture_review"] = 0
state["last_architecture_review_finalizer"] = {
    "epic": epic,
    "slice_id": slice_id,
    "run_id": run_id,
}
path.write_text(json.dumps(state, indent=2) + "\n")
PY
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

# Validate the semantic interface between an architecture review and the
# corrective work it admits. Numeric convergence metrics alone are too
# shallow: every finding needs a stable identity, a retained reproducer, and
# an exact corrective-slice closure contract before the review may merge.
ralph_validate_architecture_review_manifest() {
  local packet="${1:?review packet is required}" worktree="${2:?worktree is required}"
  local closed="${3:-}" critical="${4:-}" high="${5:-}" medium="${6:-}" low="${7:-}"
  python3 - "$packet" "$worktree" \
    "$closed" "$critical" "$high" "$medium" "$low" <<'PY'
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

worktree = Path(sys.argv[2]).resolve()
packet_path = Path(sys.argv[1]).resolve()
try:
    packet_relative = packet_path.relative_to(worktree)
except ValueError:
    raise SystemExit("Architecture-review packet is outside the candidate worktree.")
expected_evidence_prefix = (packet_relative.parent / "evidence").as_posix().rstrip("/") + "/"
try:
    expected_metrics = tuple(int(value) for value in sys.argv[3:8])
except ValueError as exc:
    raise SystemExit(f"Architecture-review manifest metrics must be integers: {exc}")

FINDING_HEADERS = [
    "Finding ID",
    "Root ID",
    "Severity",
    "Disposition",
    "Reproducer",
    "Corrective Slice",
    "Closure Evidence",
]
SLICE_HEADERS = ["Finding ID", "Root ID", "Reproducer", "Acceptance IDs"]
ID_RE = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+){2,}$")
SLICE_RE = re.compile(r"^(?:[0-9]{3}[A-Za-z0-9]*|CR-[0-9]{3,})$")
AC_RE = re.compile(r"^AC-[A-Z0-9]+(?:-[A-Z0-9]+)*$")
RED_RE = re.compile(
    r"(?im)^\s*(?:FAILED(?:\s|:)|FAIL:|AssertionError(?:\s|:)|Exit code:\s*[1-9][0-9]*)"
)
ZERO_EXIT_RE = re.compile(r"(?im)^Exit code:\s*0\s*$")
PASS_SIGNAL_RE = re.compile(r"(?im)(\b[1-9][0-9]* passed\b|^PASS:|^OK(?:\s|$))")


def successful_evidence(text: str) -> bool:
    return (
        ZERO_EXIT_RE.search(text) is not None
        and PASS_SIGNAL_RE.search(text) is not None
        and RED_RE.search(text) is None
    )


def section(text: str, heading: str) -> list[str] | None:
    matches = list(re.finditer(rf"(?m)^## {re.escape(heading)}\s*$", text))
    if len(matches) != 1:
        return None
    start = matches[0].end()
    tail = text[start:]
    next_heading = re.search(r"(?m)^## ", tail)
    if next_heading:
        tail = tail[: next_heading.start()]
    return [line.strip() for line in tail.splitlines() if line.strip()]


def table(lines: list[str] | None, headers: list[str], label: str) -> list[dict[str, str]]:
    if lines is None:
        raise SystemExit(f"Missing exact '## {label}' section.")
    if lines == ["- None"]:
        return []
    if len(lines) < 2:
        raise SystemExit(f"{label} must contain a Markdown table or '- None'.")

    def cells(line: str) -> list[str]:
        if not line.startswith("|") or not line.endswith("|"):
            raise SystemExit(f"{label} contains a malformed table row: {line}")
        return [cell.strip() for cell in line[1:-1].split("|")]

    actual_headers = cells(lines[0])
    if actual_headers != headers:
        raise SystemExit(
            f"{label} headers must be exactly: {' | '.join(headers)}"
        )
    separator = cells(lines[1])
    if len(separator) != len(headers) or any(
        not re.fullmatch(r":?-{3,}:?", cell) for cell in separator
    ):
        raise SystemExit(f"{label} has an invalid Markdown separator row.")
    rows: list[dict[str, str]] = []
    for line in lines[2:]:
        values = cells(line)
        if len(values) != len(headers) or any(not value for value in values):
            raise SystemExit(f"{label} contains an incomplete row: {line}")
        rows.append(dict(zip(headers, values)))
    if not rows:
        raise SystemExit(f"{label} must use '- None' when it has no rows.")
    return rows


def safe_file(base: Path, value: str, label: str) -> Path:
    pure = PurePosixPath(value)
    if value in {"", "-"} or pure.is_absolute() or ".." in pure.parts:
        raise SystemExit(f"{label} must be a safe relative file path: {value}")
    candidate = (base / Path(*pure.parts)).resolve()
    try:
        candidate.relative_to(base)
    except ValueError:
        raise SystemExit(f"{label} escapes the worktree: {value}")
    if not candidate.is_file() or candidate.stat().st_size == 0:
        raise SystemExit(f"{label} is missing or empty: {value}")
    return candidate


def durable_candidate_file(value: str, label: str) -> Path:
    if not value.startswith(expected_evidence_prefix):
        raise SystemExit(
            f"{label} must live under this review run's retained evidence tree "
            f"({expected_evidence_prefix}): {value}"
        )
    candidate = safe_file(worktree, value, label)
    tracked = subprocess.run(
        ["git", "-C", str(worktree), "ls-files", "--error-unmatch", "--", value],
        text=True,
        capture_output=True,
        check=False,
    ).returncode == 0
    visible = subprocess.run(
        ["git", "-C", str(worktree), "status", "--porcelain", "--untracked-files=all", "--", value],
        text=True,
        capture_output=True,
        check=False,
    ).stdout.strip()
    if not tracked and not visible:
        raise SystemExit(f"{label} is ignored or absent from the commit candidate: {value}")
    return candidate


def head_review_findings() -> str:
    result = subprocess.run(
        ["git", "-C", str(worktree), "show", "HEAD:docs/working/REVIEW_FINDINGS.md"],
        text=True,
        capture_output=True,
        check=False,
    )
    return result.stdout if result.returncode == 0 else ""


def retained_finding(text: str, finding_id: str, root_id: str) -> bool:
    matches = list(re.finditer(rf"(?m)^## {re.escape(finding_id)}(?:\s|$)", text))
    if len(matches) != 1:
        return False
    tail = text[matches[0].end():]
    next_heading = re.search(r"(?m)^## ", tail)
    if next_heading:
        tail = tail[: next_heading.start()]
    return re.search(rf"(?m)^Root: {re.escape(root_id)}\s*$", tail) is not None


def finding_id_exists(text: str, finding_id: str) -> bool:
    return re.search(rf"(?m)^## {re.escape(finding_id)}(?:\s|$)", text) is not None


def finding_sections(text: str, label: str) -> tuple[dict[str, str], str]:
    matches = list(re.finditer(r"(?m)^## ([A-Z][A-Z0-9]*(?:-[A-Z0-9]+){2,})(?:\s.*)?$", text))
    sections: dict[str, str] = {}
    spans: list[tuple[int, int]] = []
    for index, match in enumerate(matches):
        finding_id = match.group(1)
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        next_heading = re.search(r"(?m)^## ", text[match.end():end])
        if next_heading:
            end = match.end() + next_heading.start()
        if finding_id in sections:
            raise SystemExit(f"{label} repeats stable finding id: {finding_id}")
        sections[finding_id] = text[match.start():end].strip()
        spans.append((match.start(), end))
    remainder_parts = []
    cursor = 0
    for start, end in spans:
        remainder_parts.append(text[cursor:start])
        cursor = end
    remainder_parts.append(text[cursor:])
    remainder = "".join(remainder_parts)
    return sections, remainder


def root_ids(text: str) -> set[str]:
    return set(re.findall(r"(?m)^Root: ([A-Z][A-Z0-9]*(?:-[A-Z0-9]+){2,})\s*$", text))


def labelled_acceptance_ids(text: str, slice_id: str) -> set[str]:
    headings = list(re.finditer(r"(?m)^## Acceptance Criteria\s*$", text))
    if not headings:
        raise SystemExit(f"Corrective slice has no Acceptance Criteria: {slice_id}")
    ids: set[str] = set()
    for index, match in enumerate(headings):
        start = match.end()
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        next_heading = re.search(r"(?m)^## ", text[start:end])
        if next_heading:
            end = start + next_heading.start()
        for line in text[start:end].splitlines():
            stripped = line.strip()
            if not re.match(r"^(?:-|[0-9]+\.)\s+", stripped):
                continue
            criterion = re.match(r"^(?:-|[0-9]+\.)\s+\[(AC-[A-Z0-9]+(?:-[A-Z0-9]+)*)\]\s+", stripped)
            if not criterion:
                raise SystemExit(
                    f"Every corrective acceptance criterion needs an [AC-*] label: {slice_id}: {stripped}"
                )
            acceptance_id = criterion.group(1)
            if acceptance_id in ids:
                raise SystemExit(f"Corrective slice repeats acceptance id {acceptance_id}: {slice_id}")
            ids.add(acceptance_id)
    if not ids:
        raise SystemExit(f"Corrective slice has no labelled acceptance criteria: {slice_id}")
    return ids


def resolve_slice(slice_id: str) -> Path:
    if not SLICE_RE.fullmatch(slice_id):
        raise SystemExit(f"Invalid corrective slice id in finding manifest: {slice_id}")
    matches = sorted((worktree / "docs/slices").glob(f"{slice_id}-*.md"))
    if len(matches) != 1:
        raise SystemExit(
            f"Corrective slice must resolve exactly once for finding manifest: {slice_id}"
        )
    status_lines = matches[0].read_text().splitlines()
    try:
        index = status_lines.index("## Status")
        status = status_lines[index + 1].strip()
    except (ValueError, IndexError):
        raise SystemExit(f"Corrective slice has no readable Status: {slice_id}")
    if status not in {"Not Started", "Blocked"}:
        raise SystemExit(f"Corrective slice is not actionable: {slice_id} ({status})")
    return matches[0]


packet_text = packet_path.read_text()
rows = table(section(packet_text, "Finding Closure Manifest"), FINDING_HEADERS, "Finding Closure Manifest")
candidate_findings_path = worktree / "docs/working/REVIEW_FINDINGS.md"
candidate_findings = candidate_findings_path.read_text() if candidate_findings_path.is_file() else ""
head_findings = head_review_findings()
candidate_sections, candidate_remainder = finding_sections(candidate_findings, "candidate REVIEW_FINDINGS.md")
head_sections, head_remainder = finding_sections(head_findings, "fixed-point REVIEW_FINDINGS.md")
if candidate_remainder != head_remainder:
    raise SystemExit(
        "REVIEW_FINDINGS.md changes must be confined to stable finding-ID sections."
    )
manifest_ids = {row["Finding ID"] for row in rows}
changed_ledger_ids = {
    finding_id
    for finding_id in set(candidate_sections) | set(head_sections)
    if candidate_sections.get(finding_id) != head_sections.get(finding_id)
}
if manifest_ids != changed_ledger_ids:
    raise SystemExit(
        "Finding manifest and changed REVIEW_FINDINGS.md sections must match exactly: "
        f"manifest={sorted(manifest_ids)}, ledger={sorted(changed_ledger_ids)}"
    )
seen_findings: set[str] = set()
seen_roots: set[str] = set()
prior_roots = root_ids(head_findings)
derived = {"closed": 0, "Critical": 0, "High": 0, "Medium": 0, "Low": 0}

for row in rows:
    finding_id = row["Finding ID"]
    root_id = row["Root ID"]
    severity = row["Severity"]
    disposition = row["Disposition"]
    reproducer = row["Reproducer"]
    corrective = row["Corrective Slice"]
    closure = row["Closure Evidence"]

    if not ID_RE.fullmatch(finding_id) or not ID_RE.fullmatch(root_id):
        raise SystemExit(f"Finding and root IDs must be stable uppercase IDs: {finding_id} / {root_id}")
    if finding_id in seen_findings:
        raise SystemExit(f"Finding appears more than once in manifest: {finding_id}")
    seen_findings.add(finding_id)
    if root_id in seen_roots:
        raise SystemExit(f"Root appears more than once in finding manifest: {root_id}")
    seen_roots.add(root_id)
    if severity not in {"Critical", "High", "Medium", "Low"}:
        raise SystemExit(f"Invalid finding severity for {finding_id}: {severity}")
    if disposition not in {"New", "Carried", "Closed"}:
        raise SystemExit(f"Invalid finding disposition for {finding_id}: {disposition}")
    reproducer_path = durable_candidate_file(reproducer, f"Reproducer for {finding_id}")
    reproducer_text = reproducer_path.read_text(errors="replace")
    if not re.search(rf"(?m)^Finding ID: {re.escape(finding_id)}\s*$", reproducer_text) or not re.search(
        rf"(?m)^Root ID: {re.escape(root_id)}\s*$", reproducer_text
    ):
        raise SystemExit(f"Reproducer is not bound to finding/root identity: {finding_id}")
    if severity in {"Critical", "High"} and not RED_RE.search(reproducer_text):
        raise SystemExit(f"Critical/High reproducer has no failing signal: {finding_id}")

    if not retained_finding(candidate_findings, finding_id, root_id):
        raise SystemExit(
            f"REVIEW_FINDINGS.md must retain one section for {finding_id} with exact root {root_id}."
        )
    existed = finding_id_exists(head_findings, finding_id)
    if disposition == "New" and existed:
        raise SystemExit(f"New finding ID already existed before this review: {finding_id}")
    if disposition == "New" and root_id in prior_roots:
        raise SystemExit(
            f"New finding attempts to relabel an existing root instead of carrying it: {root_id}"
        )
    if disposition in {"Carried", "Closed"} and not retained_finding(
        head_findings, finding_id, root_id
    ):
        raise SystemExit(
            f"{disposition} finding has no prior stable identity/root pair: {finding_id} / {root_id}"
        )

    if disposition == "Closed":
        derived["closed"] += 1
        if corrective != "-":
            raise SystemExit(f"Closed finding must not admit corrective work: {finding_id}")
        closure_path = durable_candidate_file(closure, f"Closure evidence for {finding_id}")
        closure_text = closure_path.read_text(errors="replace")
        if not re.search(rf"(?m)^Finding ID: {re.escape(finding_id)}\s*$", closure_text) or not re.search(
            rf"(?m)^Root ID: {re.escape(root_id)}\s*$", closure_text
        ):
            raise SystemExit(f"Closure evidence is not bound to finding/root identity: {finding_id}")
        if not successful_evidence(closure_text):
            raise SystemExit(
                f"Closure evidence needs a positive pass, explicit zero exit, and no failure signal: {finding_id}"
            )
        continue

    if closure != "-":
        raise SystemExit(f"Open finding must not claim closure evidence: {finding_id}")
    if disposition == "New":
        derived[severity] += 1
    if severity in {"Critical", "High"} and corrective == "-":
        raise SystemExit(f"Open {severity} finding has no corrective slice: {finding_id}")
    if corrective == "-":
        continue

    slice_path = resolve_slice(corrective)
    slice_rows = table(
        section(slice_path.read_text(), "Review Finding Closure"),
        SLICE_HEADERS,
        "Review Finding Closure",
    )
    matches = [item for item in slice_rows if item["Finding ID"] == finding_id]
    if len(matches) != 1:
        raise SystemExit(
            f"Corrective slice {corrective} must declare finding {finding_id} exactly once."
        )
    contract = matches[0]
    manifest_slice_ids = {
        item["Finding ID"] for item in rows if item["Corrective Slice"] == corrective
    }
    contract_slice_ids = {item["Finding ID"] for item in slice_rows}
    if manifest_slice_ids != contract_slice_ids:
        raise SystemExit(
            f"Corrective slice {corrective} finding ids do not exactly match its manifest mappings."
        )
    if contract["Root ID"] != root_id or contract["Reproducer"] != reproducer:
        raise SystemExit(
            f"Corrective slice {corrective} changed the root or reproducer for {finding_id}."
        )
    acceptance_ids = [value.strip() for value in contract["Acceptance IDs"].split(",")]
    if not acceptance_ids or any(not AC_RE.fullmatch(value) for value in acceptance_ids):
        raise SystemExit(
            f"Corrective slice {corrective} has invalid acceptance IDs for {finding_id}."
        )
    declared_for_slice = {
        value.strip()
        for item in slice_rows
        for value in item["Acceptance IDs"].split(",")
    }
    all_acceptance_ids = [
        value.strip()
        for item in slice_rows
        for value in item["Acceptance IDs"].split(",")
    ]
    if len(all_acceptance_ids) != len(set(all_acceptance_ids)):
        raise SystemExit(
            f"Corrective slice {corrective} assigns an acceptance id to multiple findings."
        )
    labelled_for_slice = labelled_acceptance_ids(slice_path.read_text(), corrective)
    if declared_for_slice != labelled_for_slice:
        raise SystemExit(
            f"Corrective slice {corrective} closure contract does not cover every labelled acceptance criterion."
        )

actual_metrics = (
    derived["closed"],
    derived["Critical"],
    derived["High"],
    derived["Medium"],
    derived["Low"],
)
if actual_metrics != expected_metrics:
    raise SystemExit(
        "Finding manifest does not match convergence metrics: "
        f"manifest={actual_metrics}, metrics={expected_metrics}"
    )
print(f"PASS: validated {len(rows)} stable finding manifest row(s).")
PY
}

# A corrective slice that carries a Review Finding Closure table cannot pass
# merely because the existing suite is green. The run must retain the original
# RED signal, the permanent GREEN regression, and evidence for every declared
# acceptance id through one machine-readable artifact.
ralph_validate_review_finding_closure() {
  local worktree="${1:?worktree is required}" slice_file="${2:?slice file is required}"
  local run_dir="${3:?run directory is required}"
  python3 - "$worktree" "$slice_file" "$run_dir" <<'PY'
import ast
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

worktree = Path(sys.argv[1]).resolve()
slice_path = Path(sys.argv[2]).resolve()
run_dir = Path(sys.argv[3]).resolve()
closure_path = run_dir / "review-closure-evidence.md"

SLICE_HEADERS = ["Finding ID", "Root ID", "Reproducer", "Acceptance IDs"]
FINDING_HEADERS = ["Finding ID", "Root ID", "Permanent Test", "RED Evidence", "GREEN Evidence"]
AC_HEADERS = ["Acceptance ID", "Test", "Evidence"]
ID_RE = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+){2,}$")
AC_RE = re.compile(r"^AC-[A-Z0-9]+(?:-[A-Z0-9]+)*$")
RED_RE = re.compile(
    r"(?im)^\s*(?:FAILED(?:\s|:)|FAIL:|AssertionError(?:\s|:)|Exit code:\s*[1-9][0-9]*)"
)
ZERO_EXIT_RE = re.compile(r"(?im)^Exit code:\s*0\s*$")
PASS_SIGNAL_RE = re.compile(r"(?im)(\b[1-9][0-9]* passed\b|^PASS:|^OK(?:\s|$))")


def successful_evidence(text: str) -> bool:
    return (
        ZERO_EXIT_RE.search(text) is not None
        and PASS_SIGNAL_RE.search(text) is not None
        and RED_RE.search(text) is None
    )


def section(text: str, heading: str) -> list[str] | None:
    matches = list(re.finditer(rf"(?m)^## {re.escape(heading)}\s*$", text))
    if len(matches) != 1:
        return None
    tail = text[matches[0].end():]
    next_heading = re.search(r"(?m)^## ", tail)
    if next_heading:
        tail = tail[: next_heading.start()]
    return [line.strip() for line in tail.splitlines() if line.strip()]


def table(lines: list[str] | None, headers: list[str], label: str) -> list[dict[str, str]]:
    if lines is None or len(lines) < 3:
        raise SystemExit(f"Missing or empty exact '## {label}' table.")

    def cells(line: str) -> list[str]:
        if not line.startswith("|") or not line.endswith("|"):
            raise SystemExit(f"{label} contains a malformed row: {line}")
        return [cell.strip() for cell in line[1:-1].split("|")]

    if cells(lines[0]) != headers:
        raise SystemExit(f"{label} headers must be exactly: {' | '.join(headers)}")
    separator = cells(lines[1])
    if len(separator) != len(headers) or any(
        not re.fullmatch(r":?-{3,}:?", cell) for cell in separator
    ):
        raise SystemExit(f"{label} has an invalid Markdown separator row.")
    rows = []
    for line in lines[2:]:
        values = cells(line)
        if len(values) != len(headers) or any(not value for value in values):
            raise SystemExit(f"{label} contains an incomplete row: {line}")
        rows.append(dict(zip(headers, values)))
    if not rows:
        raise SystemExit(f"{label} contains no evidence rows.")
    return rows


def safe_file(base: Path, value: str, label: str) -> Path:
    pure = PurePosixPath(value)
    if not value or pure.is_absolute() or ".." in pure.parts:
        raise SystemExit(f"{label} must be a safe relative path: {value}")
    candidate = (base / Path(*pure.parts)).resolve()
    try:
        candidate.relative_to(base)
    except ValueError:
        raise SystemExit(f"{label} escapes its evidence root: {value}")
    if not candidate.is_file() or candidate.stat().st_size == 0:
        raise SystemExit(f"{label} is missing or empty: {value}")
    return candidate


def candidate_visible(candidate: Path, label: str) -> None:
    try:
        relative = candidate.relative_to(worktree).as_posix()
    except ValueError:
        raise SystemExit(f"{label} is outside the candidate worktree.")
    tracked = subprocess.run(
        ["git", "-C", str(worktree), "ls-files", "--error-unmatch", "--", relative],
        text=True,
        capture_output=True,
        check=False,
    ).returncode == 0
    visible = subprocess.run(
        ["git", "-C", str(worktree), "status", "--porcelain", "--untracked-files=all", "--", relative],
        text=True,
        capture_output=True,
        check=False,
    ).stdout.strip()
    if not tracked and not visible:
        raise SystemExit(f"{label} is ignored or absent from the commit candidate: {relative}")


def validate_test_spec(value: str, label: str) -> None:
    if "::" not in value:
        raise SystemExit(f"{label} must bind a permanent test file to an exact selector: {value}")
    path_value, selector = value.split("::", 1)
    if not selector.strip():
        raise SystemExit(f"{label} has an empty test selector: {value}")
    test_path = safe_file(worktree, path_value, label)
    candidate_visible(test_path, label)
    relative = test_path.relative_to(worktree).as_posix()
    source = test_path.read_text(errors="replace")
    if test_path.suffix == ".py":
        if not (test_path.name.startswith("test_") or "/tests/" in f"/{relative}"):
            raise SystemExit(f"{label} is not a discoverable Python test path: {value}")
        selector_parts = selector.replace("::", ".").split(".")
        selector_parts[-1] = re.sub(r"\[.*\]$", "", selector_parts[-1])
        if any(not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", part) for part in selector_parts):
            raise SystemExit(f"{label} has an invalid Python selector: {value}")
        try:
            nodes = ast.parse(source).body
        except SyntaxError:
            raise SystemExit(f"{label} points to a Python test file with invalid syntax: {value}")
        selected = None
        for index, part in enumerate(selector_parts):
            selected = next(
                (
                    node for node in nodes
                    if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
                    and node.name == part
                ),
                None,
            )
            if selected is None:
                break
            nodes = selected.body if isinstance(selected, ast.ClassDef) else []
            if index < len(selector_parts) - 1 and not isinstance(selected, ast.ClassDef):
                selected = None
                break
        test_name = selector_parts[-1]
        if (
            selected is None
            or not isinstance(selected, (ast.FunctionDef, ast.AsyncFunctionDef))
            or not test_name.startswith("test_")
        ):
            raise SystemExit(f"{label} selector is absent from its Python test file: {value}")
    elif test_path.suffix in {".ts", ".tsx", ".js", ".jsx"}:
        if not re.search(r"\.(?:test|spec)\.(?:ts|tsx|js|jsx)$", test_path.name):
            raise SystemExit(f"{label} is not a discoverable frontend test path: {value}")
        typescript_module = next(
            (
                parent / "node_modules/typescript/lib/typescript.js"
                for parent in test_path.parents
                if parent == worktree or worktree in parent.parents
                if (parent / "node_modules/typescript/lib/typescript.js").is_file()
            ),
            None,
        )
        if typescript_module is None:
            raise SystemExit(f"{label} cannot resolve frontend syntax without TypeScript: {value}")
        parser = r'''const ts = require(process.argv[1]);
const fs = require("fs");
const filename = process.argv[2];
const expected = process.argv[3];
const source = fs.readFileSync(filename, "utf8");
const unit = ts.createSourceFile(filename, source, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);
if (unit.parseDiagnostics.length) process.exit(2);
const modifiers = new Set(["only", "concurrent"]);
const factories = new Set(["each"]);
function isDirectTestCallee(node) {
  if (ts.isIdentifier(node)) return node.text === "test" || node.text === "it";
  if (ts.isPropertyAccessExpression(node)) {
    return modifiers.has(node.name.text) && isDirectTestCallee(node.expression);
  }
  return false;
}
function isFactoryCallee(node) {
  return ts.isPropertyAccessExpression(node)
    && factories.has(node.name.text)
    && isDirectTestCallee(node.expression);
}
function isTestDeclaration(node) {
  if (isDirectTestCallee(node.expression)) return true;
  return ts.isCallExpression(node.expression) && isFactoryCallee(node.expression.expression);
}
let found = false;
function visit(node) {
  if (ts.isCallExpression(node) && isTestDeclaration(node)) {
    const title = node.arguments[0];
    if (title && ts.isStringLiteralLike(title) && title.text === expected) found = true;
  }
  ts.forEachChild(node, visit);
}
visit(unit);
process.exit(found ? 0 : 1);
'''
        parsed = subprocess.run(
            ["node", "-e", parser, str(typescript_module), str(test_path), selector],
            text=True,
            capture_output=True,
            check=False,
        )
        if parsed.returncode != 0:
            raise SystemExit(f"{label} selector is absent from its frontend test file: {value}")
    elif test_path.suffix == ".sh":
        if not relative.startswith("scripts/tests/") or "regression" not in test_path.name:
            raise SystemExit(f"{label} is not a Ralph regression test path: {value}")
        shell_function = re.compile(
            rf"(?m)^\s*(?:function\s+)?{re.escape(selector)}\s*(?:\(\s*\))?\s*\{{"
        )
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", selector) or not shell_function.search(source):
            raise SystemExit(f"{label} selector is absent from its shell test file: {value}")
    else:
        raise SystemExit(f"{label} does not identify an executable test file: {value}")


def labelled_acceptance_ids(text: str) -> set[str]:
    headings = list(re.finditer(r"(?m)^## Acceptance Criteria\s*$", text))
    if not headings:
        raise SystemExit("Corrective slice has no Acceptance Criteria section.")
    ids: set[str] = set()
    for index, match in enumerate(headings):
        start = match.end()
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        next_heading = re.search(r"(?m)^## ", text[start:end])
        if next_heading:
            end = start + next_heading.start()
        for line in text[start:end].splitlines():
            stripped = line.strip()
            if not re.match(r"^(?:-|[0-9]+\.)\s+", stripped):
                continue
            criterion = re.match(r"^(?:-|[0-9]+\.)\s+\[(AC-[A-Z0-9]+(?:-[A-Z0-9]+)*)\]\s+", stripped)
            if not criterion:
                raise SystemExit(
                    f"Every corrective acceptance criterion needs an [AC-*] label: {stripped}"
                )
            acceptance_id = criterion.group(1)
            if acceptance_id in ids:
                raise SystemExit(f"Corrective slice repeats acceptance id: {acceptance_id}")
            ids.add(acceptance_id)
    if not ids:
        raise SystemExit("Corrective slice has no labelled acceptance criteria.")
    return ids


candidate_slice_text = slice_path.read_text()
try:
    slice_relative = slice_path.relative_to(worktree).as_posix()
except ValueError:
    raise SystemExit("Selected corrective slice is outside the candidate worktree.")
head_result = subprocess.run(
    ["git", "-C", str(worktree), "show", f"HEAD:{slice_relative}"],
    text=True,
    capture_output=True,
    check=False,
)
if head_result.returncode != 0:
    raise SystemExit("Selected corrective slice has no trusted fixed-point version.")
head_slice_text = head_result.stdout
head_slice_lines = section(head_slice_text, "Review Finding Closure")
candidate_slice_lines = section(candidate_slice_text, "Review Finding Closure")
if head_slice_lines is None:
    if candidate_slice_lines is not None:
        raise SystemExit("Candidate added an untrusted review-finding closure contract.")
    print("PASS: slice has no architecture-review finding closure contract.")
    raise SystemExit(0)
if candidate_slice_text != head_slice_text:
    raise SystemExit(
        "Candidate changed or removed the fixed-point corrective slice contract."
    )
slice_rows = table(head_slice_lines, SLICE_HEADERS, "Review Finding Closure")
if not closure_path.is_file() or closure_path.stat().st_size == 0:
    raise SystemExit("review-closure-evidence.md is required for a corrective finding slice.")
closure_text = closure_path.read_text()
finding_rows = table(section(closure_text, "Finding Evidence"), FINDING_HEADERS, "Finding Evidence")
acceptance_rows = table(section(closure_text, "Acceptance Evidence"), AC_HEADERS, "Acceptance Evidence")

contracts: dict[str, dict[str, object]] = {}
expected_acceptance: set[str] = set()
for row in slice_rows:
    finding_id = row["Finding ID"]
    root_id = row["Root ID"]
    if not ID_RE.fullmatch(finding_id) or not ID_RE.fullmatch(root_id):
        raise SystemExit(f"Invalid stable finding/root id in corrective slice: {finding_id} / {root_id}")
    if finding_id in contracts:
        raise SystemExit(f"Corrective slice repeats finding id: {finding_id}")
    acceptance_ids = [value.strip() for value in row["Acceptance IDs"].split(",")]
    if not acceptance_ids or any(not AC_RE.fullmatch(value) for value in acceptance_ids):
        raise SystemExit(f"Invalid acceptance ids for corrective finding {finding_id}.")
    overlap = expected_acceptance.intersection(acceptance_ids)
    if overlap:
        raise SystemExit(f"Acceptance ids must belong to one finding only: {sorted(overlap)}")
    expected_acceptance.update(acceptance_ids)
    contracts[finding_id] = {"root": root_id, "acceptance": set(acceptance_ids)}
labelled_acceptance = labelled_acceptance_ids(head_slice_text)
if labelled_acceptance != expected_acceptance:
    raise SystemExit(
        "Review Finding Closure acceptance ids do not exactly cover the labelled Acceptance Criteria."
    )

seen_findings: set[str] = set()
for row in finding_rows:
    finding_id = row["Finding ID"]
    if finding_id not in contracts or finding_id in seen_findings:
        raise SystemExit(f"Finding Evidence has an unknown or duplicate id: {finding_id}")
    seen_findings.add(finding_id)
    if row["Root ID"] != contracts[finding_id]["root"]:
        raise SystemExit(f"Finding Evidence changed the root id for {finding_id}.")
    test_spec = row["Permanent Test"]
    validate_test_spec(test_spec, f"Permanent test for {finding_id}")
    red_path = safe_file(run_dir, row["RED Evidence"], f"RED evidence for {finding_id}")
    green_path = safe_file(run_dir, row["GREEN Evidence"], f"GREEN evidence for {finding_id}")
    if not row["RED Evidence"].startswith("evidence/") or not row["GREEN Evidence"].startswith("evidence/"):
        raise SystemExit(f"RED/GREEN evidence must live under the current run's evidence/: {finding_id}")
    candidate_visible(red_path, f"RED evidence for {finding_id}")
    candidate_visible(green_path, f"GREEN evidence for {finding_id}")
    if red_path == green_path:
        raise SystemExit(f"RED and GREEN evidence must be distinct for {finding_id}.")
    red_text = red_path.read_text(errors="replace")
    green_text = green_path.read_text(errors="replace")
    if test_spec not in red_text or test_spec not in green_text:
        raise SystemExit(f"RED/GREEN evidence is not bound to the permanent test selector: {finding_id}")
    if not RED_RE.search(red_text):
        raise SystemExit(f"RED evidence has no failing signal for {finding_id}.")
    if not successful_evidence(green_text):
        raise SystemExit(
            f"GREEN evidence needs a positive pass, explicit zero exit, and no failure signal for {finding_id}."
        )
if seen_findings != set(contracts):
    missing = sorted(set(contracts) - seen_findings)
    raise SystemExit(f"Finding Evidence is missing corrective findings: {missing}")

seen_acceptance: set[str] = set()
for row in acceptance_rows:
    acceptance_id = row["Acceptance ID"]
    if acceptance_id not in expected_acceptance or acceptance_id in seen_acceptance:
        raise SystemExit(f"Acceptance Evidence has an unknown or duplicate id: {acceptance_id}")
    seen_acceptance.add(acceptance_id)
    test_spec = row["Test"]
    validate_test_spec(test_spec, f"Acceptance test for {acceptance_id}")
    evidence_path = safe_file(run_dir, row["Evidence"], f"Acceptance evidence for {acceptance_id}")
    if not row["Evidence"].startswith("evidence/"):
        raise SystemExit(f"Acceptance evidence must live under the current run's evidence/: {acceptance_id}")
    candidate_visible(evidence_path, f"Acceptance evidence for {acceptance_id}")
    evidence_text = evidence_path.read_text(errors="replace")
    if test_spec not in evidence_text:
        raise SystemExit(f"Acceptance evidence is not bound to its exact test selector: {acceptance_id}")
    if not successful_evidence(evidence_text):
        raise SystemExit(
            f"Acceptance evidence needs a positive pass, explicit zero exit, and no failure signal for {acceptance_id}."
        )
if seen_acceptance != expected_acceptance:
    missing = sorted(expected_acceptance - seen_acceptance)
    raise SystemExit(f"Acceptance Evidence is missing declared ids: {missing}")

print(
    f"PASS: validated semantic closure for {len(contracts)} finding(s) "
    f"and {len(expected_acceptance)} acceptance id(s)."
)
PY
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
