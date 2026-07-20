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

ralph_architecture_review_auto_finalizer_policy_enabled() {
  local config="${1:?config is required}" approvals_file="${2:?approvals file is required}"
  local maximum
  maximum="$(awk -F': *' '/^[[:space:]]*architecture_review_max_corrective_generations:/ {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' "$config" | xargs || true)"
  maximum="${maximum:-2}"
  [[ "$maximum" =~ ^[1-9][0-9]*$ ]] || return 1
  grep -qF -- \
    "- [approved-finalizer-policy] generation $maximum | one terminal finalizer per Root ID |" \
    "$approvals_file"
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
  # A due review may yield only to the exact first grabbable owner-approved
  # finalizer for a genuinely exhausted root. Ordinary same-Epic work remains
  # blocked, so cadence reviews cannot fail open.
  if ralph_queue_first_slice_is_approved_architecture_finalizer \
      "$state_file" "$slice_dir"; then
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

ralph_queue_first_slice_is_approved_architecture_finalizer() {
  local state_file="${1:?state file is required}" slice_dir="${2:?slice directory is required}"
  local config approvals first
  config="$(dirname "$state_file")/config.yaml"
  approvals="$(dirname "$slice_dir")/working/HIGH_RISK_APPROVALS.md"
  [[ -f "$config" && -f "$approvals" ]] || return 1
  first="$(ralph_first_grabbable_slice "$slice_dir" || true)"
  [[ -n "$first" ]] || return 1
  ralph_architecture_review_finalizer_contract \
    "$config" "$state_file" "$slice_dir/$first" "$approvals" >/dev/null
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

ralph_architecture_review_root_transition() {
  local mode="${1:?mode is required}" state_file="${2:?state file is required}"
  local packet="${3:?review packet is required}" maximum="${4:-}"
  local slice_dir="${5:-}" approvals_file="${6:-}"
  [[ "$mode" == "validate" || "$mode" == "apply" ]] || return 1
  [[ -f "$state_file" && -f "$packet" ]] || return 1
  if [[ "$mode" == "validate" ]] \
      && ! [[ "$maximum" =~ ^[1-9][0-9]*$ ]]; then
    echo "Invalid architecture-review convergence configuration." >&2
    return 1
  fi
  python3 - "$mode" "$state_file" "$packet" "${maximum:-0}" \
    "$slice_dir" "$approvals_file" <<'PY'
import json
import os
import re
import sys
from pathlib import Path

mode, state_name, packet_name, maximum_value, slice_dir_name, approvals_name = sys.argv[1:]
state_path = Path(state_name)
packet_path = Path(packet_name)
slice_dir = Path(slice_dir_name) if slice_dir_name else None
approvals_path = Path(approvals_name) if approvals_name else None

try:
    state = json.loads(state_path.read_text())
except (OSError, json.JSONDecodeError) as exc:
    raise SystemExit(f"Invalid architecture-review state: {exc}")

roots = state.get("architecture_review_root_generations", {})
if not isinstance(roots, dict):
    raise SystemExit("architecture_review_root_generations must be an object")
for root_id, value in roots.items():
    if not isinstance(value, dict) or not isinstance(value.get("generation"), int):
        raise SystemExit(f"Invalid per-root convergence state: {root_id}")
    if value["generation"] < 1 or not isinstance(value.get("corrective_slice"), str):
        raise SystemExit(f"Invalid per-root convergence state: {root_id}")

lines = packet_path.read_text().splitlines()
try:
    start = lines.index("## Finding Closure Manifest") + 1
except ValueError:
    raise SystemExit("Review packet has no Finding Closure Manifest")

rows = []
for line in lines[start:]:
    if line.startswith("## "):
        break
    if not line.startswith("|"):
        continue
    values = [item.strip() for item in line.strip().strip("|").split("|")]
    if values and values[0] in {"Finding ID", "---"}:
        continue
    if len(values) != 7:
        raise SystemExit("Finding Closure Manifest row has the wrong number of columns")
    rows.append(values)

updated = {key: dict(value) for key, value in roots.items()}
maximum = int(maximum_value)
terminal_roots = state.get("architecture_review_terminal_roots", [])
if not isinstance(terminal_roots, list) or not all(isinstance(item, str) for item in terminal_roots):
    raise SystemExit("architecture_review_terminal_roots must be a string list")

def section_value(text, heading):
    lines = text.splitlines()
    try:
        index = lines.index(heading) + 1
    except ValueError:
        return ""
    while index < len(lines) and not lines[index].strip():
        index += 1
    return lines[index].strip() if index < len(lines) and not lines[index].startswith("## ") else ""

def standing_terminal_finalizer(root_id, corrective, current_generation, epic):
    if slice_dir is None or approvals_path is None or root_id in terminal_roots:
        return False
    if current_generation != maximum:
        return False
    if not approvals_path.is_file():
        return False
    policy = (
        f"- [approved-finalizer-policy] generation {maximum} | "
        "one terminal finalizer per Root ID |"
    )
    if not any(line.startswith(policy) for line in approvals_path.read_text().splitlines()):
        return False
    if not re.fullmatch(r"CR-[0-9]{3,}", corrective):
        return False
    matches = list(slice_dir.glob(f"{corrective}-*.md"))
    if len(matches) != 1:
        return False
    text = matches[0].read_text()
    if section_value(text, "## Status") != "Not Started":
        return False
    if section_value(text, "## Risk Level") != "High":
        return False
    parent = section_value(text, "## Parent Epic")
    if re.search(rf"\bEpic {re.escape(epic)}\b", parent) is None:
        return False
    lines = text.splitlines()
    try:
        start = lines.index("## Architecture Review Finalizer") + 1
    except ValueError:
        return False
    fields = {}
    while start < len(lines) and not lines[start].startswith("## "):
        line = lines[start].strip()
        if line:
            match = re.fullmatch(r"- (Epic|Root ID|Exhausted corrective generation): (.+)", line)
            if not match or match.group(1) in fields:
                return False
            fields[match.group(1)] = match.group(2)
        start += 1
    return fields == {
        "Epic": epic,
        "Root ID": root_id,
        "Exhausted corrective generation": str(current_generation),
    }

for finding_id, root_id, severity, disposition, _reproducer, corrective, _closure in rows:
    if disposition == "Closed":
        updated.pop(root_id, None)
        continue
    if severity not in {"Critical", "High"} or corrective == "-":
        continue
    if root_id in terminal_roots:
        raise SystemExit(
            f"TERMINAL_RECURRENCE: architecture review root {root_id} already "
            "consumed its one owner-preauthorized terminal finalizer."
        )
    epic_match = re.fullmatch(r"ROOT-([0-9]{3})-[A-Z0-9-]+", root_id)
    if not epic_match:
        raise SystemExit(f"Convergence root has no canonical Epic identity: {root_id}")
    current = updated.get(root_id)
    generation = int(current.get("generation", 0)) if current else 0
    if current is None or current.get("corrective_slice") != corrective:
        generation += 1
    if generation > maximum:
        if standing_terminal_finalizer(
            root_id, corrective, int(current.get("generation", 0)), epic_match.group(1)
        ):
            generation = int(current["generation"])
        else:
            raise SystemExit(
                f"Architecture review root {root_id} exceeded the {maximum}-generation "
                "corrective cap; refusing another successor."
            )
    updated[root_id] = {
        "epic": epic_match.group(1),
        "generation": generation,
        "corrective_slice": corrective,
        "finding_id": finding_id,
        "severity": severity,
    }

if mode == "apply":
    state["architecture_review_root_generations"] = updated
    state.pop("architecture_review_cycle_epic", None)
    state.pop("architecture_review_corrective_generation", None)
    temporary = state_path.with_name(f"{state_path.name}.tmp.{os.getpid()}")
    temporary.write_text(json.dumps(state, indent=2) + "\n")
    temporary.replace(state_path)
PY
}

ralph_validate_architecture_review_convergence() {
  local config="${1:?config is required}" state_file="${2:?state file is required}"
  local packet="${3:?review packet is required}" slice_dir="${4:-}"
  local approvals_file="${5:-}" maximum
  maximum="$(awk -F': *' '/^[[:space:]]*architecture_review_max_corrective_generations:/ {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' "$config" | xargs || true)"
  maximum="${maximum:-2}"
  local output rc=0
  output="$(ralph_architecture_review_root_transition \
    validate "$state_file" "$packet" "$maximum" "$slice_dir" "$approvals_file" \
    2>&1)" || rc=$?
  [[ -n "$output" ]] && printf '%s\n' "$output" >&2
  if (( rc != 0 )) && printf '%s\n' "$output" | grep -q '^TERMINAL_RECURRENCE:'; then
    return "${RALPH_EXIT_REVIEW_TERMINAL_RECURRENCE:-28}"
  fi
  return "$rc"
}

ralph_apply_architecture_review_root_transitions() {
  local config state_file packet slice_dir approvals_file maximum
  if [[ "${1:-}" == *.json ]]; then
    state_file="${1:?state file is required}"
    packet="${2:?review packet is required}"
    config="$(dirname "$state_file")/config.yaml"
    slice_dir="${3:-}"
    approvals_file="${4:-}"
  else
    config="${1:?config is required}"
    state_file="${2:?state file is required}"
    packet="${3:?review packet is required}"
    slice_dir="${4:-}"
    approvals_file="${5:-}"
  fi
  maximum="$(awk -F': *' '/^[[:space:]]*architecture_review_max_corrective_generations:/ {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' "$config" 2>/dev/null | xargs || true)"
  maximum="${maximum:-2}"
  ralph_architecture_review_root_transition \
    apply "$state_file" "$packet" "$maximum" "$slice_dir" "$approvals_file"
}

# Validate the narrow owner-controlled exit for an exhausted corrective cycle.
# A slice declaration is insufficient: the protected approvals file must name
# the exact CR, epic, and generation, and durable state must prove the configured
# corrective-generation cap has actually been reached.
ralph_architecture_review_finalizer_contract() {
  local config="${1:?config is required}" state_file="${2:?state file is required}"
  local slice_file="${3:?slice file is required}" approvals_file="${4:?approvals file is required}"
  local allow_review_transition="${5:-false}"
  local base slice_id approval_id fields epic root generation maximum state_values
  local due state_epic state_generation terminal_seen risk parent
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
    inside && /^- Root ID: / {
      root_count += 1
      root = $0
      sub(/^- Root ID: /, "", root)
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
      if (sections == 1 && epic_count == 1 && root_count == 1 && generation_count == 1 && unknown == 0) {
        print epic "\t" root "\t" generation
      }
    }
  ' "$slice_file")"
  IFS=$'\t' read -r epic root generation <<< "$fields"
  [[ "$epic" =~ ^[0-9][0-9][0-9]$ \
      && "$root" =~ ^ROOT-${epic}-[A-Z0-9-]+$ \
      && "$generation" =~ ^[1-9][0-9]*$ ]] || return 1
  maximum="$(awk -F': *' '/^[[:space:]]*architecture_review_max_corrective_generations:/ {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' "$config" | xargs || true)"
  maximum="${maximum:-2}"
  [[ "$maximum" =~ ^[1-9][0-9]*$ ]] || return 1
  state_values="$(python3 - "$state_file" "$root" <<'PY'
import json
import sys

try:
    state = json.load(open(sys.argv[1]))
    due = state.get("architecture_review_due")
    root = sys.argv[2]
    entry = state.get("architecture_review_root_generations", {}).get(root, {})
    epic = entry.get("epic", "")
    generation = int(entry.get("generation", 0))
    terminal = root in state.get("architecture_review_terminal_roots", [])
except (OSError, TypeError, ValueError, json.JSONDecodeError):
    raise SystemExit(1)
if not isinstance(due, bool) or not isinstance(epic, str):
    raise SystemExit(1)
print(f"{'True' if due else 'False'}\t{epic}\t{generation}\t{'True' if terminal else 'False'}")
PY
)" || return 1
  IFS=$'\t' read -r due state_epic state_generation terminal_seen <<< "$state_values"
  [[ ( "$due" == "True" || "$allow_review_transition" == "true" ) \
      && "$state_epic" == "$epic" \
      && "$state_generation" == "$generation" && "$terminal_seen" == "False" ]] || return 1
  (( generation == maximum )) || return 1
  parent="$(ralph_slice_parent_epics "$(dirname "$slice_file")" "$slice_id")"
  printf '%s\n' "$parent" | grep -Fxq "$epic" || return 1
  if ! grep -qF -- \
      "- [approved-finalizer] $approval_id | Epic $epic | Root $root | generation $generation |" \
      "$approvals_file"; then
    grep -qF -- \
      "- [approved-finalizer-policy] generation $maximum | one terminal finalizer per Root ID |" \
      "$approvals_file" || return 1
  fi
  printf '%s\t%s\n' "$epic" "$root"
}

# A successful review normally clears its due flag. When that same validated
# review admitted a standing-policy terminal finalizer, immediately restore a
# narrow barrier that yields only to the exact first grabbable finalizer.
ralph_mark_architecture_review_terminal_finalizer_due() {
  local config="${1:?config is required}" state_file="${2:?state file is required}"
  local slice_dir="${3:?slice directory is required}"
  local approvals_file="${4:?approvals file is required}" first contract epic root
  first="$(ralph_first_grabbable_slice "$slice_dir" || true)"
  [[ -n "$first" ]] || return 0
  contract="$(ralph_architecture_review_finalizer_contract \
    "$config" "$state_file" "$slice_dir/$first" "$approvals_file" true 2>/dev/null || true)"
  [[ -n "$contract" ]] || return 0
  IFS=$'\t' read -r epic root <<< "$contract"
  python3 - "$state_file" "$root" <<'PY'
import json
import os
import sys
from pathlib import Path

path = Path(sys.argv[1])
state = json.loads(path.read_text())
state["architecture_review_due"] = True
state["architecture_review_due_reason"] = f"terminal_finalizer:{sys.argv[2]}"
temporary = path.with_name(f"{path.name}.tmp.{os.getpid()}")
temporary.write_text(json.dumps(state, indent=2) + "\n")
temporary.replace(path)
PY
}

# Compatibility name for callers that only need to test whether the contract
# is valid. New callers should retain both the Epic and Root ID.
ralph_architecture_review_finalizer_epic() {
  ralph_architecture_review_finalizer_contract "$@" | cut -f1
}

# Apply the trusted post-validation transition. Only the orchestrator calls
# this after every declared product gate passes; candidate content cannot grant
# itself authority to clear an exhausted architecture-review cycle.
ralph_finalize_architecture_review_cycle() {
  local state_file="${1:?state file is required}" epic="${2:?epic is required}"
  local root="${3:?root id is required}" slice_id="${4:?slice id is required}"
  local run_id="${5:?run id is required}"
  [[ "$epic" =~ ^[0-9][0-9][0-9]$ \
      && "$root" =~ ^ROOT-${epic}-[A-Z0-9-]+$ \
      && "$slice_id" =~ ^CR-[0-9][A-Za-z0-9._-]*$ \
      && "$run_id" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]] || return 1
  python3 - "$state_file" "$epic" "$root" "$slice_id" "$run_id" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
epic, root, slice_id, run_id = sys.argv[2:]
approval_match = __import__("re").match(r"^(CR-[0-9]+)", slice_id)
if approval_match is None:
    raise SystemExit("architecture-review finalizer has no CR approval identity")
approval_id = approval_match.group(1)
state = json.loads(path.read_text())
if state.get("architecture_review_due") is not True:
    raise SystemExit("architecture-review finalizer requires a due review")
roots = state.get("architecture_review_root_generations", {})
entry = roots.get(root)
if not isinstance(entry, dict) or entry.get("epic") != epic:
    raise SystemExit("architecture-review finalizer root does not match the active Epic")
if int(entry.get("generation", 0)) < 1:
    raise SystemExit("architecture-review finalizer requires an exhausted root generation")
terminal_roots = state.get("architecture_review_terminal_roots", [])
if not isinstance(terminal_roots, list) or root in terminal_roots:
    raise SystemExit("architecture-review root already consumed its terminal finalizer")
closed_roots = sorted(
    root_id for root_id, value in roots.items()
    if root_id == root or (
        isinstance(value, dict) and value.get("corrective_slice") == approval_id
    )
)
for root_id in closed_roots:
    roots.pop(root_id, None)
state["architecture_review_root_generations"] = roots
state["architecture_review_terminal_roots"] = sorted(terminal_roots + [root])
state["architecture_review_due"] = False
state.pop("architecture_review_due_reason", None)
state.pop("architecture_review_cycle_epic", None)
state.pop("architecture_review_corrective_generation", None)
state["slices_completed_since_architecture_review"] = 0
state["last_architecture_review_finalizer"] = {
    "epic": epic,
    "root_id": root,
    "root_ids": closed_roots,
    "slice_id": slice_id,
    "run_id": run_id,
}
path.write_text(json.dumps(state, indent=2) + "\n")
PY
}

ralph_architecture_review_scope_instruction() {
  local state_file="${1:?state file is required}"
  python3 - "$state_file" <<'PY'
import json, sys
try:
    state = json.load(open(sys.argv[1]))
except (OSError, json.JSONDecodeError):
    raise SystemExit(0)
roots = state.get("architecture_review_root_generations", {})
if isinstance(roots, dict) and roots:
    budgets = ", ".join(
        f"{root}=generation {entry.get('generation', '?')} via {entry.get('corrective_slice', '?')}"
        for root, entry in sorted(roots.items())
        if isinstance(entry, dict)
    )
    print(
        f"- Trusted per-root corrective history: {budgets}. Review the new product diff and these "
        "active roots only. Preserve every stable Finding ID/Root ID, never charge a new root for "
        "another root's history, and never relabel a carried symptom as New. A root may receive at "
        "most one grouped corrective plus one successor; unrelated roots retain independent budgets."
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
    # Preserve blank lines: in Markdown they terminate a table. Human-readable
    # notes after that boundary are not additional machine-readable rows.
    return [line.strip() for line in tail.splitlines()]


def table(lines: list[str] | None, headers: list[str], label: str) -> list[dict[str, str]]:
    if lines is None:
        raise SystemExit(f"Missing or empty exact '## {label}' table.")
    lines = list(lines)
    while lines and not lines[0]:
        lines.pop(0)
    if len(lines) < 3:
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
    table_ended = False
    for line in lines[2:]:
        if not line:
            if rows:
                table_ended = True
            continue
        if table_ended:
            continue
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
    if "::" in value:
        path_value, selector = value.split("::", 1)
    else:
        # Django's native dotted test labels are exact executable selectors.
        # Resolve the longest importable file prefix, then validate the
        # remaining class/function path through the same AST checks below.
        dotted = value.split(".")
        if len(dotted) < 2 or any(
            not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", part)
            for part in dotted
        ):
            raise SystemExit(
                f"{label} must bind a permanent test file to an exact selector: {value}"
            )
        path_value = ""
        selector = ""
        for split_at in range(len(dotted) - 1, 0, -1):
            candidate_value = "/".join(dotted[:split_at]) + ".py"
            if (worktree / candidate_value).is_file():
                path_value = candidate_value
                selector = "::".join(dotted[split_at:])
                break
        if not path_value or not selector:
            raise SystemExit(
                f"{label} has an unresolved Django test selector: {value}"
            )
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

# Count new executable corrective slices. Ordinary review work remains numeric;
# a CR-NNN file is admitted only when it is the exact standing-policy terminal
# finalizer for an already exhausted root.
ralph_architecture_review_new_corrective_count() {
  local worktree="${1:?worktree is required}" path base status count=0
  while IFS= read -r path; do
    [[ -n "$path" ]] || continue
    base="$(basename "$path")"
    if ! [[ "$base" =~ ^[0-9][0-9][0-9][A-Za-z0-9]*-.+\.md$ ]]; then
      if ! [[ "$base" =~ ^CR-[0-9][0-9][0-9][0-9]*-.+\.md$ ]] \
          || ! ralph_architecture_review_finalizer_contract \
            "$worktree/.ralph/config.yaml" "$worktree/.ralph/state.json" \
            "$worktree/$path" "$worktree/docs/working/HIGH_RISK_APPROVALS.md" \
            true >/dev/null; then
        echo "New corrective slice is neither numeric nor an approved terminal finalizer: $base" >&2
        return 1
      fi
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
