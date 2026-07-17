#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/../lib/ralph-exit-protocol.sh"
source "$script_dir/../lib/ralph-runtime-capabilities.sh"
source "$script_dir/../lib/ralph-agent-log.sh"

for assignment in "$@"; do
  export "$assignment"
done

: "${RUN_ID:?RUN_ID is required}"
: "${RUN_DIR:?RUN_DIR is required}"
: "${WORKTREE_DIR:?WORKTREE_DIR is required}"
: "${PROMPT_FILE:?PROMPT_FILE is required}"
SELECTED_SLICE="${SELECTED_SLICE:-}"

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
slice_file="$WORKTREE_DIR/docs/slices/${SELECTED_SLICE}.md"
if [[ -n "$SELECTED_SLICE" && ! -f "$slice_file" ]]; then
  echo "Selected slice file is missing: $slice_file" >&2
  exit 1
fi
CODEX_PERMISSION_PROFILE="$(ralph_codex_permission_profile_for_slice "$slice_file")"
codex_sandbox_label="permission-profile"

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
- Sandbox mode: $codex_sandbox_label
- Permission profile: ${CODEX_PERMISSION_PROFILE:-none}
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
if [[ "$CODEX_PERMISSION_PROFILE" == "ralph-postgres" ]]; then
  # Permission profiles and --sandbox are mutually exclusive. This profile
  # preserves workspace isolation while allowing only PostgreSQL's test socket.
  # Repeat the profile as launch overrides so dynamic nested worktree trust
  # discovery cannot cause Codex to ignore the project-scoped definition.
  args+=(-c 'permissions.ralph-postgres.extends=":workspace"')
  args+=(-c 'permissions.ralph-postgres.network.enabled=true')
  args+=(-c 'permissions.ralph-postgres.network.unix_sockets={"/tmp/.s.PGSQL.5432"="allow"}')
  args+=(-c "default_permissions=\"$CODEX_PERMISSION_PROFILE\"")
elif [[ "$CODEX_PERMISSION_PROFILE" == "ralph-localhost" ]]; then
  # E2E browser suites need to bind and connect only to the local Django/Vite
  # servers. Keep normal internet destinations unavailable.
  args+=(-c 'permissions.ralph-localhost.extends=":workspace"')
  args+=(-c 'permissions.ralph-localhost.network.enabled=true')
  args+=(-c 'permissions.ralph-localhost.network.domains={"localhost"="allow","127.0.0.1"="allow"}')
  args+=(-c "default_permissions=\"$CODEX_PERMISSION_PROFILE\"")
elif [[ "$CODEX_PERMISSION_PROFILE" == "ralph-postgres-localhost" ]]; then
  # Compose both declared local capabilities without granting general network
  # access or changing the default profile for ordinary slices.
  args+=(-c 'permissions.ralph-postgres-localhost.extends=":workspace"')
  args+=(-c 'permissions.ralph-postgres-localhost.network.enabled=true')
  args+=(-c 'permissions.ralph-postgres-localhost.network.domains={"localhost"="allow","127.0.0.1"="allow"}')
  args+=(-c 'permissions.ralph-postgres-localhost.network.unix_sockets={"/tmp/.s.PGSQL.5432"="allow"}')
  args+=(-c "default_permissions=\"$CODEX_PERMISSION_PROFILE\"")
else
  # Repeat the workspace profile at launch so nested Ralph worktrees never
  # fall back to read-only when project trust/config discovery changes.
  args+=(-c 'default_permissions=":workspace"')
fi

# Watchdog: a hung agent must fail the run (into the repair path), not
# stall the loop forever. Pure bash — macOS has no GNU timeout.
timeout_secs="${AGENT_TIMEOUT_SECONDS:-7200}"
if ! [[ "$timeout_secs" =~ ^[0-9]+$ ]]; then
  echo "WARN: AGENT_TIMEOUT_SECONDS is not a number ('$timeout_secs'); using 7200." >&2
  timeout_secs=7200
fi
ralph_prepare_agent_log "$WORKTREE_DIR" "$RUN_ID" codex
log="$RALPH_AGENT_RAW_LOG"
summary_log="$RUN_DIR/evidence/terminal-logs/codex-summary.md"

codex "${args[@]}" $CODEX_ADDITIONAL_ARGS < "$PROMPT_FILE" > "$log" 2>&1 &
agent_pid=$!

# The full transcript is short-lived operator-local evidence outside the Git
# candidate. Committed run evidence receives only a bounded excerpt and hash.
echo "Full agent log: $log (bounded local retention)"
(
  heartbeat_seconds="${RALPH_AGENT_HEARTBEAT_SECONDS:-30}"
  while kill -0 "$agent_pid" 2>/dev/null; do
    sleep "$heartbeat_seconds"
    kill -0 "$agent_pid" 2>/dev/null || break
    log_bytes="$(wc -c < "$log" 2>/dev/null | xargs || echo 0)"
    echo "Codex agent active (PID $agent_pid, full log ${log_bytes} bytes)."
  done
) &
heartbeat_pid=$!

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
pkill -P "$heartbeat_pid" 2>/dev/null || true
kill "$heartbeat_pid" 2>/dev/null || true
wait "$heartbeat_pid" 2>/dev/null || true
ralph_write_agent_log_summary "$log" "$summary_log" codex "$status"
echo "Codex agent finished with exit $status. Final log excerpt:"
tail -n 30 "$log" 2>/dev/null | cut -c1-500 || true

# Flag usage-limit exhaustion so the loop can switch agents. Only a failed
# agent whose final log lines name a usage/rate limit counts — a genuine
# coding failure must keep following the normal repair path.
if (( status != 0 )) && tail -n 40 "$log" | grep -qiE "usage limit|rate limit|limit (reached|exceeded)|quota (reached|exceeded)|too many requests"; then
  echo "AGENT_LIMIT_EXHAUSTED: codex exited $status and its log tail names a usage limit."
  {
    echo "# Agent Limit Exhausted"
    echo
    echo "codex exited $status; the log tail names a usage/rate limit. See evidence/terminal-logs/codex-summary.md."
  } > "$RUN_DIR/agent-limit-exhausted.md"
  exit "$RALPH_EXIT_AGENT_LIMIT"
fi

exit "$status"
