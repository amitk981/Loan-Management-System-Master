#!/usr/bin/env bash

# Stable process outcomes for communication between Ralph wrappers. Agent output
# is untrusted diagnostic text and must never be parsed to decide control flow.
readonly RALPH_EXIT_SUCCESS=0
readonly RALPH_EXIT_FAILED=1
readonly RALPH_EXIT_QUEUE_EMPTY=20
readonly RALPH_EXIT_OWNER_VETO=21
readonly RALPH_EXIT_MERGE_FAILED=22
readonly RALPH_EXIT_AGENT_LIMIT=23
readonly RALPH_EXIT_QUEUE_BLOCKED=24
readonly RALPH_EXIT_BROWSER_INFRASTRUCTURE=25
readonly RALPH_EXIT_ITERATION_LIMIT=26

ralph_outcome_for_status() {
  case "${1:?status is required}" in
    "$RALPH_EXIT_SUCCESS") echo "success" ;;
    "$RALPH_EXIT_QUEUE_EMPTY") echo "queue_empty" ;;
    "$RALPH_EXIT_OWNER_VETO") echo "owner_veto" ;;
    "$RALPH_EXIT_MERGE_FAILED") echo "merge_failed" ;;
    "$RALPH_EXIT_AGENT_LIMIT") echo "agent_limit" ;;
    "$RALPH_EXIT_QUEUE_BLOCKED") echo "queue_blocked" ;;
    "$RALPH_EXIT_BROWSER_INFRASTRUCTURE") echo "browser_infrastructure" ;;
    "$RALPH_EXIT_ITERATION_LIMIT") echo "iteration_limit" ;;
    *) echo "failed" ;;
  esac
}
