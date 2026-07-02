#!/usr/bin/env bash
set -euo pipefail

for assignment in "$@"; do
  export "$assignment"
done

: "${RUN_ID:?RUN_ID is required}"
: "${RUN_DIR:?RUN_DIR is required}"
: "${WORKTREE_DIR:?WORKTREE_DIR is required}"
: "${PROMPT_FILE:?PROMPT_FILE is required}"

if ! command -v claude >/dev/null 2>&1; then
  echo "claude command is not installed." >&2
  exit 1
fi

CLAUDE_MODEL="${CLAUDE_MODEL:-}"

mkdir -p "$RUN_DIR/evidence/terminal-logs"

cat > "$RUN_DIR/claude-settings.md" <<EOF
# Claude Settings

- AGENT_TOOL: claude
- Surface: CLI headless (-p)
- Requested model: ${CLAUDE_MODEL:-CLI default}
- Permissions: bypassed (unattended AFK run inside isolated worktree under standing approval)
- Config source: environment overrides
EOF

cd "$WORKTREE_DIR"

args=(-p --dangerously-skip-permissions)
if [[ -n "$CLAUDE_MODEL" ]]; then
  args+=(--model "$CLAUDE_MODEL")
fi

# Watchdog: a hung agent must fail the run (into the repair path), not
# stall the loop forever. Pure bash — macOS has no GNU timeout.
timeout_secs="${AGENT_TIMEOUT_SECONDS:-7200}"
log="$RUN_DIR/evidence/terminal-logs/claude.log"

claude "${args[@]}" < "$PROMPT_FILE" > "$log" 2>&1 &
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
