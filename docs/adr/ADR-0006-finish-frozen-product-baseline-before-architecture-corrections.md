# ADR-0006: Finish the Frozen Product Baseline Before Architecture Corrections

## Status
Accepted

## Context
Periodic architecture discovery had become a self-extending queue: reviews added corrective slices, those corrections triggered further verification reviews, and the original product tail stopped advancing. On 2026-07-22 the owner chose to finish the 39 slices that existed before `010N6`–`010N8`, then consolidate architecture discovery and implement the accepted findings.

## Decision
Ralph may carry one explicit, owner-frozen completion baseline in `.ralph/state.json`. While that baseline is active, only its listed slices are selectable and ordinary cadence, Epic-boundary, High-finding, finalizer, and terminal-repair review barriers are deferred. Critical findings remain fail-closed and are never deferred. When the last baseline slice completes, Ralph moves the baseline to `awaiting_review` and requires one consolidated architecture review before review-generated corrections can resume.

## Consequences
- The baseline is an exact list, not a filename range or mutable queue query; later review findings cannot silently join or reorder it.
- `010N6`, `010N7`, and `010N8` remain durable findings and executable corrections, but they run only after the consolidated review.
- Normal per-slice tests, typecheck, lint, build, risk gates, and fixed-spec review remain mandatory throughout the baseline.
- A malformed, missing, dependency-blocked, or completed-but-unreviewed baseline fails closed instead of falling through to unrelated work.
