#!/usr/bin/env bash

# Keep each Ralph agent session in one role. The runner may ask this module
# which role applies and for the role's architecture instructions; callers do
# not need to understand the review state machine.

ralph_prompt_role() {
  local mode="${1:?mode is required}" split_slice_id="${2:-}" state_file="${3:-}"

  if [[ -n "$split_slice_id" ]]; then
    printf 'queue_rewrite\n'
    return 0
  fi
  case "$mode" in
    normal|normal_run)
      printf 'implementation\n'
      ;;
    repair)
      printf 'repair\n'
      ;;
    architecture_review)
      python3 - "$state_file" <<'PY'
import json
import sys
from pathlib import Path

try:
    state = json.loads(Path(sys.argv[1]).read_text())
except (IndexError, OSError, json.JSONDecodeError) as exc:
    raise SystemExit(f"Cannot classify architecture-review prompt: {exc}")

reason = state.get("architecture_review_due_reason", "")
repairs = state.get("architecture_review_terminal_repairs", {})
awaiting_terminal_verification = isinstance(repairs, dict) and any(
    isinstance(record, dict) and record.get("status") == "awaiting_verification"
    for record in repairs.values()
)
closure_reason = isinstance(reason, str) and any(
    part.startswith(("terminal_repair:", "terminal_repair_verification:", "terminal_finalizer:"))
    for part in reason.split("+")
)
print("review_closure" if closure_reason or awaiting_terminal_verification else "review_discovery")
PY
      ;;
    *)
      printf 'Unsupported Ralph prompt mode: %s\n' "$mode" >&2
      return 2
      ;;
  esac
}

ralph_prompt_architecture_instruction() {
  local role="${1:?prompt role is required}"
  case "$role" in
    implementation|repair)
      return 0
      ;;
    review_closure)
      cat <<'EOF'
- This is closure verification, not architecture discovery. Review only the inherited Finding ID/Root ID pairs and their exact bound reproducers. Do not discover new findings, inspect unrelated product diffs, relabel a carried symptom, or propose unrelated queue work. A finding closes only when its original command passes through the documented public seam with current bound evidence. If an inherited finding still reproduces, preserve its stable identity and use only the exact bounded successor or quarantine transition already authorized by the supplied scope; do not invent another corrective generation. Report the exact convergence metrics with every New severity set to 0. Do not modify production code.
EOF
      ;;
    review_discovery)
      cat <<'EOF'
- In architecture-discovery mode: do NOT modify production code. Review only the fixed diffs merged since the prior architecture checkpoint as an independent critic: test quality (real assertions and edge cases), source-document fidelity, duplication, and architecture drift. Append validated findings to docs/working/REVIEW_FINDINGS.md. Only Critical/High correctness, security, financial/data-integrity, or binding source-contract findings create immediate corrective work. Bundle Medium findings into the owning epic closure and record Low findings unless they naturally combine with higher-severity work. Group related symptoms by root owner instead of creating one slice per symptom. Report findings closed, new findings by severity, and corrective slices added in review-packet.md under '## Convergence Metrics' using the exact lines '- Findings closed: N', '- New Critical: N', '- New High: N', '- New Medium: N', '- New Low: N', and '- Corrective slices added: N'. A normal new corrective must be a numeric Not Started slice with a valid Depends On contract. Exception: when the scope instruction says a carried root is already at the configured generation cap and it genuinely needs a different successor, create exactly one next-numbered CR-NNN terminal finalizer instead of another numeric leaf. Its filename may add a descriptive slug, but every Finding Closure Manifest row must use the CR-NNN identity. It must be Not Started, High risk, owned by the same Parent Epic, group every related Critical/High root into its Review Finding Closure contract, and contain exactly '## Architecture Review Finalizer' followed by '- Epic: NNN', '- Root ID: ROOT-NNN-*', and '- Exhausted corrective generation: N'. The standing owner policy admits only one such terminal CR per root. If executable evidence later disproves that finalizer, preserve the same stable findings and roots and group them into one correction; the orchestrator may rewrite it as one bounded same-finalizer repair episode, never generation 3 or a second finalizer. Product gates leave that episode open until a later independent review explicitly closes every inherited Finding ID/Root ID pair. A genuine later regression opens the next bounded episode on the same stable identities. After the configured episode cap, a further reproduced terminal finding uses disposition Quarantined with no corrective or closure evidence; it becomes a release blocker while unrelated queued slices continue. When an actionable existing root-owner slice already covers a new Critical/High finding, do not duplicate it; add one exact '- Existing corrective slice: ID' line per mapped slice under the convergence metrics. Validation requires every mapped ID to resolve to one tracked Not Started or Blocked slice. If corrective additions exceed closures across two reviews, recommend one root-cause seam correction instead of further leaf patches.
- A terminal recurrence-repair successor may depend only on slices that are already Complete or Superseded. Never place it behind unfinished unrelated work or rename it merely to sort first: after authentication, the orchestrator gives that exact pending repair bounded priority over ordinary grabbable slices.
EOF
      ;;
    queue_rewrite)
      return 0
      ;;
    *)
      printf 'Unsupported Ralph prompt role: %s\n' "$role" >&2
      return 2
      ;;
  esac
}
