#!/usr/bin/env bash
set -euo pipefail

for assignment in "$@"; do
  export "$assignment"
done

: "${RUN_ID:?RUN_ID is required}"
: "${RUN_DIR:?RUN_DIR is required}"
: "${WORKTREE_DIR:?WORKTREE_DIR is required}"
: "${PROMPT_FILE:?PROMPT_FILE is required}"

if ! command -v codex >/dev/null 2>&1; then
  echo "codex command is not installed." >&2
  exit 1
fi

CODEX_PROFILE="${CODEX_PROFILE:-default}"
CODEX_REASONING_EFFORT="${CODEX_REASONING_EFFORT:-medium}"
CODEX_VERBOSITY="${CODEX_VERBOSITY:-medium}"
CODEX_APPROVAL_MODE="${CODEX_APPROVAL_MODE:-never}"
CODEX_MODEL="${CODEX_MODEL:-}"
CODEX_ADDITIONAL_ARGS="${CODEX_ADDITIONAL_ARGS:-exec}"

mkdir -p "$RUN_DIR/evidence/terminal-logs"

cat > "$RUN_DIR/codex-settings.md" <<EOF
# Codex Settings

- AGENT_TOOL: codex
- Codex surface used: CLI
- Codex profile: $CODEX_PROFILE
- Requested model: ${CODEX_MODEL:-Codex CLI default}
- Actual model if known: unknown
- Requested reasoning effort: $CODEX_REASONING_EFFORT
- Actual reasoning effort if known: unknown
- Verbosity setting: $CODEX_VERBOSITY
- Approval mode: $CODEX_APPROVAL_MODE
- Fallback used: no
- Config source: .ralph/config.yaml and environment overrides
EOF

cd "$WORKTREE_DIR"

args=()
if [[ -n "$CODEX_MODEL" ]]; then
  args+=(--model "$CODEX_MODEL")
fi
args+=(-c "model_reasoning_effort=$CODEX_REASONING_EFFORT")
args+=(-c "model_verbosity=$CODEX_VERBOSITY")
args+=(--ask-for-approval "$CODEX_APPROVAL_MODE")

# Watchdog: a hung agent must fail the run (into the repair path), not
# stall the loop forever. Pure bash — macOS has no GNU timeout.
timeout_secs="${AGENT_TIMEOUT_SECONDS:-7200}"
if ! [[ "$timeout_secs" =~ ^[0-9]+$ ]]; then
  echo "WARN: AGENT_TIMEOUT_SECONDS is not a number ('$timeout_secs'); using 7200." >&2
  timeout_secs=7200
fi
log="$RUN_DIR/evidence/terminal-logs/codex.log"

codex "${args[@]}" $CODEX_ADDITIONAL_ARGS < "$PROMPT_FILE" > "$log" 2>&1 &
agent_pid=$!
(
  sleep "$timeout_secs"
  echo "WATCHDOG: agent exceeded ${timeout_secs}s; terminating." >> "$log"
  kill -TERM "$agent_pid" 2>/dev/null || true
  sleep 30
  kill -KILL "$agent_pid" 2>/dev/null || true
) &
watchdog_pid=$!

status=0
wait "$agent_pid" || status=$?
kill "$watchdog_pid" 2>/dev/null || true
wait "$watchdog_pid" 2>/dev/null || true

cat "$log"
exit "$status"
