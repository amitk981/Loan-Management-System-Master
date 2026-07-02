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

claude "${args[@]}" < "$PROMPT_FILE" 2>&1 | tee "$RUN_DIR/evidence/terminal-logs/claude.log"
