# Ralph Handoff

## Last Run
2026-07-13_202809_normal_run

## Current Status

007F2 is complete. Non-forced exception routing now rejects contradictory frozen amount/flag facts
before matrix resolution or enrichment writes. A truthful above-limit route remains visible and
actionable with independently authored sanction and Exception Register reasons; a retained public
tracer covers submission, enrichment, ordinary/assigned reads, CFO plus two Director approval,
Exception Register closure, sanction decision, and terminal Credit Sanction Register generation.

Exception coherence now binds the same case/application/register identity, business reason, type,
risk shape, frozen amount-limit predicate, matrix condition, two-Director authority, and register
requirement. The case detail exposes frozen `exception_reason`; `reason_for_approval` remains the
sanction decision reason. Exact replay is zero-write and changed immutable facts conflict.

The appraisal `post_save` projection receiver is removed. Approval coherence and exact reader
indexing are invoked explicitly by approval-owned submission/linkage, enrichment, and action
writers. Direct appraisal/case saves do not mutate cross-table projection state, and later live
appraisal changes do not rewrite frozen historical-cycle authority. No migration or new assumption
was required.

The remaining architecture-review corrections are still queued in dependency order:

1. `007G2-general-meeting-current-evidence-and-document-scope-closure`
2. `007H2-sanction-decision-and-register-object-scope-closure`

007G2 and 007H2 were sharpened with 007F2's delivered reason/projection contract. 007I remains
blocked by those corrections. A-085 remains open for 007G2 to resolve.

## Validation

Retained RED/GREEN logs cover the contradictory reason invariant, frozen exception predicate, and
hidden appraisal-save projection mutation. The 128 affected approval tests pass. Frontend build,
typecheck, lint, and all 208 tests pass. Backend check and migration sync pass; the complete 670-test
suite passes with 19 expected PostgreSQL-only SQLite skips and 93% coverage. Diff whitespace and
protected/source path checks pass. The orchestrator will run independent validation.

## Next Run

Run `007G2`, then `007H2`. Resume `007I-sanction-workbench-ui` only after those corrective
dependencies are complete. CR-004 remains an independent queued maintenance repair.
