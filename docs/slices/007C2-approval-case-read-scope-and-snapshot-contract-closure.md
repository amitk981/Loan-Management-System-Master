# Slice 007C2: Approval-Case Read Scope and Snapshot Contract Closure

## Status
Not Started

## Parent Epic
Epic 007: Sanction Approval Workflow and Registers
Epic file: `docs/epics/007-sanction-approval-workflow.md`

## Depends On
- 007C
- 007A6

## Runtime Capabilities

none

## Goal

Close the approval-case public boundary before actions land: unassigned readers cannot enumerate or
retrieve cases, only internally coherent immutable routing snapshots are actionable, and enrichment
replays must match the frozen credit provenance and §25.2 response contract.

## Source / Review References

- `docs/source/auth-permissions.md` §§15.8-15.9, §24.1, §32.1, and §37.3
- `docs/source/api-contracts.md` §§3, 6-8, 25.2-25.4, and §44
- `docs/source/data-model.md` §§15.3-15.4 and §34
- `docs/source/codebase-design.md` §§13.1, 26.1-26.3, and §27.1
- `docs/slices/007B-approval-case-creation-from-appraisal.md`
- `docs/slices/007C-cfo-and-director-threshold-routing.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-13_100911_architecture_review`

## Concrete Requirements

1. Introduce one approval-owned case object-access predicate used before both list serialization and
   detail serialization. `approvals.case.read` is necessary but not global object scope: CFO/
   Director readers see cases named in the stored required-approver snapshot, including their own
   acted history, while an unassigned Director or arbitrary custom-role permission holder cannot
   enumerate or retrieve the case. Until a separate source-backed management/audit scope is
   persisted, unrelated access defaults to denial rather than permission-implied global scope.
2. Apply object scope before pagination/counts. `assigned_to_me=true` remains the narrower pending-
   assignment filter; the ordinary collection must never become an all-case bypass. Detail denial
   uses the established nondisclosure contract and writes no audit event.
3. Make the routable predicate validate one coherent immutable snapshot: case amount/type/entity/
   decision date/exception facts agree with the stored matrix projection; required roles, director
   count, joint/register facts are complete; exactly one stored CFO and the required distinct stored
   Directors come from the committee projection; ids/versions/dates match; approver ids are unique;
   and loan-limit provenance agrees with the application, assessment id, and exception condition.
   Do not query live rule/committee/user membership to rebuild authority.
4. A malformed or contradictory snapshot is not listable/retrievable/actionable and produces no
   writes. Add one independently named row for each mismatch category rather than a single opaque
   tuple loop; include arbitrary-user injection, duplicate approver, wrong role/count, amount/
   condition mismatch, and incomplete joint/register provenance.
5. Tighten 007B idempotency: before returning an enriched case as an exact replay, compare the
   locked reviewed decision date, recommended amount, loan-limit assessment/application ids,
   exception flag, calculation rule, policy id/name, and calculation time with the stored
   provenance. Changed credit provenance or reviewed facts returns stable 409 with unchanged case,
   audit, and workflow ledgers. Later effective configuration versions do not rewrite a valid
   historical snapshot.
6. Make the §25.2 success projection include source-required `current_status` while retaining only
   backwards-compatible additions. Unify or compose the sanction-handoff and approval-case
   serializers behind the approval-owned deep module so list/detail/enrichment cannot disagree on
   status, routing completeness, or provenance.
7. Replace 007B's manual-snapshot governance test with a real submit → enrich → canonical read,
   then reject one proposal, approve one later proposal, and preserve the complete enriched case
   and public projection across the 007A5/007A6 configuration ledger.

## Test Cases

- Assigned CFO/Director list/detail, acted history, unassigned Director, maker, arbitrary permission
  holder, and missing-read-permission rows with scoped counts and nondisclosure.
- For every permission-without-object-scope actor, assert the ordinary list returns no case data and
  a scope-filtered `total_count` of zero, then assert direct detail returns the canonical
  `403 OBJECT_ACCESS_DENIED`; snapshot the case/action/audit/workflow ledger around both requests.
- Contradictory stored snapshot matrix covering every mismatch in requirement 4; no enabled action
  or public row for any loser.
- Exact enrichment replay versus changed assessment/policy/review provenance, each with complete
  before/after ledgers.
- §25.2 `current_status` response and serializer parity across enrichment, list, and detail.
- Real enriched-case immutability across rejected, winning, and losing governed configuration
  decisions.

## Evidence Required

Failing unassigned-read, contradictory-route, provenance-replay, response-contract, and real-
enrichment governance rows; green focused APIs; complete before/after ledgers; and all gates.

## Risk Level
High

## Acceptance Criteria

- No permission holder can read an unrelated approval case without persisted source-backed scope.
- Only a self-consistent stored routing snapshot can enter queues, detail, or later action seams.
- Exact replay means the frozen credit provenance is identical, and §25.2 returns `current_status`.

## Run-Ahead Sharpening Review (007A6, 2026-07-13)

- In requirement 7's governed-configuration sequence, assert exact winner evidence content: the
  audit names the proposal/request, maker/checker, activated resource, and, for supersession, the
  retained predecessor's closed projection. Rejected/pending loser reason, request id, and version
  must not appear in either winner evidence row.
- Keep a full enriched-case ledger around that sequence. Rule/committee ids and versions, decision
  date, required approvers, workflow identity, and case version remain byte-for-byte unchanged.
