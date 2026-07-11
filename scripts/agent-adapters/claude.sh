#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/../lib/ralph-exit-protocol.sh"

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
if ! [[ "$timeout_secs" =~ ^[0-9]+$ ]]; then
  echo "WARN: AGENT_TIMEOUT_SECONDS is not a number ('$timeout_secs'); using 7200." >&2
  timeout_secs=7200
fi
log="$RUN_DIR/evidence/terminal-logs/claude.log"

claude "${args[@]}" < "$PROMPT_FILE" > "$log" 2>&1 &
agent_pid=$!

# Stream the agent's log to stdout while it runs so callers see live progress
# instead of silence until the run ends.
tail -n +1 -f "$log" &
tail_pid=$!

# The watchdog must be fully detached from stdout/stderr: an inherited pipe
# keeps callers that use command substitution blocked on the sleep child even
# after the agent finishes.
(
  sleep "$timeout_secs"
  echo "WATCHDOG: agent exceeded ${timeout_secs}s; terminating." >> "$log"
  kill -TERM "$agent_pid" 2>/dev/null || true
  sleep 30
  kill -KILL "$agent_pid" 2>/dev/null || true
) >/dev/null 2>&1 &
watchdog_pid=$!

status=0
wait "$agent_pid" || status=$?
# Kill the sleep child before its parent — once the parent dies the child
# re-parents to init and pkill -P can no longer find it.
pkill -P "$watchdog_pid" 2>/dev/null || true
kill "$watchdog_pid" 2>/dev/null || true
wait "$watchdog_pid" 2>/dev/null || true
sleep 1
kill "$tail_pid" 2>/dev/null || true
wait "$tail_pid" 2>/dev/null || true

# Flag usage-limit exhaustion so the loop can switch agents. Only a failed
# agent whose final log lines name a usage/rate limit counts — a genuine
# coding failure must keep following the normal repair path.
if (( status != 0 )) && tail -n 40 "$log" | grep -qiE "usage limit|rate limit|limit (reached|exceeded)|quota (reached|exceeded)|too many requests"; then
  echo "AGENT_LIMIT_EXHAUSTED: claude exited $status and its log tail names a usage limit."
  {
    echo "# Agent Limit Exhausted"
    echo
    echo "claude exited $status; the log tail names a usage/rate limit. See evidence/terminal-logs/claude.log."
  } > "$RUN_DIR/agent-limit-exhausted.md"
  exit "$RALPH_EXIT_AGENT_LIMIT"
fi

exit "$status"
