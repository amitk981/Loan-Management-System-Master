# Slice 008L5: Current Stage-4 and Response Evidence Closure

## Status
Not Started

## Parent Epics
Epic 008: Documentation, Legal Documents, and Security Package; Epic 005: Application Intake and
Completeness (portal continuation)

## Depends On
- 008L4

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Goal

Close the independently reproduced cases where an application status label substitutes for a
current terminal sanction and where missing deficiency-response workflow evidence is projected as
valid borrower truth.

## Source / Review References

- `docs/source/auth-permissions.md` §§19.2, 20.1, 21-23, and 37
- `docs/source/api-contracts.md` §§3, 6-8, 27, and 44
- `docs/source/data-model.md` §§16-17, 29-30, and 34
- `docs/source/functional-spec.md` M03-FR-010 through M03-FR-012 and M06-FR-005/018
- `docs/source/screen-spec-member-portal.md` MP11 §§10-11 and 14.3-14.4
- `docs/slices/008K5-final-evidence-authority-and-migration-closure.md`
- `docs/slices/008L4-portal-production-boundary-and-browser-proof.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-16_023011_architecture_review`

## Concrete Requirements

1. Make `applications.modules.bank_verification` consume the approval owner's current terminal
   sanctioned facts under the same application lock. `approved_by_sanction_committee` is necessary
   but never sufficient: missing/rejected/returned/replaced/malformed latest cases, a decision for
   an older cycle, or a status-only application must be nondisclosing and zero-write.
2. Freeze the exact sanction-decision and approval-case ids used by each bank decision in its
   immutable evidence/digest. Reconciliation must reject a decision whose retained ids no longer
   identify the current terminal cycle; do not infer them from the application status later.
3. Race a changed bank decision against latest-case invalidation/replacement under PostgreSQL. The
   only acceptable outcomes are a decision bound to the still-current terminal facts or a denied
   zero-artifact writer; a stale-cycle decision must never commit.
4. Replace the deficiency serializer's `responded` fallback with one canonical evidence resolver.
   A current immutable response may project `responded` only from its exact retained response event,
   and `submitted_for_review` only from the valid ordered response→resubmission chain.
5. Missing, duplicate, cross-response, wrong-workflow/entity/actor/state, reversed, or extra terminal
   response events must project a safe evidence-invalid/blocked state, disable resubmission, and
   leave the staff deficiency open. The API must not fabricate a valid business status or expose
   internal evidence ids.
6. Keep source-defined single portal upload/download audit vocabulary and all current browser/session
   behavior unchanged. This slice does not resolve deficiencies, complete Stage-4 checklist items,
   or add new borrower actions.

## Test Cases

- The architecture-review non-terminal-case and deleted-response-event probes pass unchanged.
- Public bank HTTP matrices cover status-only, missing/rejected/replaced latest case, malformed
  frozen facts, exact replay, changed replay, nondisclosure, and complete zero-write ledgers.
- Public MP11 GET/resubmit matrices cover valid responded/submitted chains plus every missing,
  duplicate, foreign, contradictory, and reordered workflow fact.
- The PostgreSQL bank-decision/latest-case race runs twice and retains exact winner/loser evidence.

## Evidence Required

Failing-first copies of both architecture-review probes; focused public API results; sanitized
responses and zero-write ledgers; twice-run PostgreSQL race; full configured gates.

## Risk Level
High

## Acceptance Criteria

- Immutable bank decisions require and retain the current terminal sanction, not a status label.
- Borrower deficiency state is projected only from a coherent retained workflow chain.
- Invalid/stale evidence is fail-closed, nondisclosing, and leaves no success side effects.
- All configured gates pass.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Database rules followed, if needed
- [ ] Permissions tested
- [ ] Audit events tested
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
