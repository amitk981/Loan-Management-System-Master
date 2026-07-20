#!/usr/bin/env bash

# Classify only outcomes that are safe to replay from the integration checkout.
# The loop performs trusted worktree recovery at every restart. Validation,
# convergence, ownership, merge, and policy failures remain hard stops.
ralph_supervisor_outcome_for_status() {
  case "${1:?status is required}" in
    0) echo complete ;;
    "${RALPH_EXIT_AGENT_LIMIT:-23}"|"${RALPH_EXIT_BROWSER_INFRASTRUCTURE:-25}"|\
      "${RALPH_EXIT_ITERATION_LIMIT:-26}"|129|137|143) echo retry ;;
    *) echo stop ;;
  esac
}
