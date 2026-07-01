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

mkdir -p "$RUN_DIR/evidence/terminal-logs"
cd "$WORKTREE_DIR"

claude < "$PROMPT_FILE" 2>&1 | tee "$RUN_DIR/evidence/terminal-logs/claude.log"
