# Ralph Handoff

## Last Run
2026-07-13_200023_architecture_review

## Current Status

The architecture review covered completed slices 007E2, 007F, 007G, and 007H in product commit
range `b32559c...78d912f`. Production code was not changed. The later `ac1846c` CR-004 intake commit
was docs-only and was excluded from product findings; its missing dependency declaration was repaired
so the queue remains valid.

The most urgent defect is a contradictory exception projection: 007F stores the Exception Register
business reason as the case exception reason, while the coherence engine requires that value to equal
the separately authored approval reason. A source-valid exception case can therefore disappear from
canonical reads and become unactionable. The existing public test also marks an amount below the
frozen eligible amount as an exception, so it does not prove the source predicate or a complete
exception lifecycle.

The review also found that sanction-decision and Credit Sanction Register reads apply named
permissions without the approval/application object boundary, General Meeting evidence accepts
arbitrary existing document ids after only a global permission check, and pending/rejected meeting
outcomes are absent from the canonical case detail. Appraisal `post_save` still hides approval
projection mutation. Findings are recorded newest-first in `docs/working/REVIEW_FINDINGS.md` and the
Epic 007 digest.

Three High-risk corrective slices are queued in dependency order:

1. `007F2-exception-routing-coherence-and-explicit-projection-closure`
2. `007G2-general-meeting-current-evidence-and-document-scope-closure`
3. `007H2-sanction-decision-and-register-object-scope-closure`

007I now depends on 007H2. Both 007I and 007J carry run-ahead requirements for the corrected scoped
read contracts. No ADR or new assumption was needed because the cited source contracts already
decide the required behavior; A-085 remains open for 007G2 to resolve.

## Validation

Independent Standards and Spec review passes were retained. Frontend build, typecheck, lint, and all
208 tests pass. Backend check and migration sync pass; the complete 669-test suite produced current
coverage data with 19 expected PostgreSQL-only SQLite skips and 93% coverage. Queue/dependency lint,
state JSON parsing, diff whitespace, and protected/production/source path inspection pass. The
worktree-local validator was not invoked because its hard-coded worktree virtualenv path is absent;
all backend commands used the mandated `/Users/amitkallapa/LMS/.ralph/venv/bin/python`, and the
orchestrator will run independent validation.

## Next Run

Run `007F2` first, then `007G2` and `007H2`. Resume `007I-sanction-workbench-ui` only after those
corrective dependencies are complete. CR-004 remains an independent queued maintenance repair.
