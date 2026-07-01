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
CODEX_APPROVAL_MODE="${CODEX_APPROVAL_MODE:-on-request}"
CODEX_MODEL="${CODEX_MODEL:-}"

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

codex "${args[@]}" ${CODEX_ADDITIONAL_ARGS:-} < "$PROMPT_FILE" 2>&1 | tee "$RUN_DIR/evidence/terminal-logs/codex.log"
