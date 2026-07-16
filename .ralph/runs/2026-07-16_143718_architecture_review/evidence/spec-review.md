# Independent Spec Review

Range: `1601a903...d519dc53`

## Critical

1. Legal readiness trusts mutable checklist/item labels and merely non-null approval ledger ids
   rather than exact current completion/approval evidence; required-but-inapplicable pending items
   also block under the current boolean expression.
2. Signature readiness filters unverified rows before `all`, allowing one open mismatch to produce
   an empty-set pass contrary to S34.
3. Security readiness uses statuses plus sparse ids rather than the coordinated terminal-evidence
   contract for exact PoA, SH-4, CDSL, and cheque facts.

## High

1. Signed-copy upload and correction/return/condition report success after generic workspace-local
   writes that no later current projection, blocker, or approval consumes.
2. Required PoA is silently actionless because the attorney is deliberately unavailable under
   A-125, but no explicit blocker explains that governed authority is absent.

Corrective mapping: 008M5 and 009D2. Worst severity: Critical. No source requirement justified an
ADR; the existing source already defines the owners, evidence, and authority seams.
