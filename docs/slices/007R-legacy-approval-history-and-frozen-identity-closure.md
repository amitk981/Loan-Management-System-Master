# Slice 007R: Legacy Approval History and Frozen Identity Closure

## Status
Not Started

## Parent Epic
Epic 007: Sanction Approval Workflow and Registers
Epic file: `docs/epics/007-sanction-approval-workflow.md`

## Depends On
- 007Q

## Runtime Capabilities

none

## Goal

Keep approval cases and formal register history created before the 007O/007Q frozen-schema
expansions readable and safely remediable, without reconstructing missing decision facts from live
application, member, appraisal, user, or communication rows.

## Source / Review References

- `docs/source/codebase-design.md` §§13.1, 26.1-26.3, and 27.1
- `docs/source/api-contracts.md` §§25.3-25.10 and §44
- `docs/source/data-model.md` §§15.3-15.6 and §34
- `docs/source/functional-spec.md` M05-FR-001, M05-FR-007, M05-FR-009, and M05-FR-011
- `docs/slices/007O-frozen-terminal-decision-and-register-source-closure.md`
- `docs/slices/007Q-register-source-fields-and-visual-evidence-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-14_064206_architecture_review`

## Concrete Requirements

1. Version the expanded frozen review package honestly. New packages must use a new schema version;
   do not reinterpret an older `approval-review-v2` object as if it contained 007O-only member,
   application-reference, or sanction-term facts.
2. Split historical readability from terminal-write completeness. A previously valid v2 case must
   retain actor-scoped detail/history and any already-created decision/register reads. Missing
   terminal facts must still fail closed before approve/reject decision or register writes. Provide
   an explicit, audited remediation path through the existing return -> correction -> independent
   review -> new-cycle workflow; never backfill frozen facts from current live owner rows.
3. Credit Sanction Register serialization must treat absent legacy `source_review_facts_json`,
   `terminal_facts_json`, approver, and communication facts as explicit null/empty values. An
   actor-scoped historical row must not raise, disappear, or gain values reconstructed from a live
   application/member/appraisal.
4. Freeze every formal approver display identity from the routed/action-time immutable package.
   Renaming a `User` after routing or after an earlier action must not change the later register row.
   Retain immutable user ids for attribution; unavailable legacy names remain null/labelled
   unavailable rather than being read from the current user profile.
5. Preserve canonical object scope, historical-cycle immutability, zero-write malformed-package
   behavior, optimistic versions, audit/workflow evidence, and existing terminal race semantics.

## Test Cases

- Persist the exact pre-007O v2 JSON shape, then upgrade code: authorised detail/history remains
  readable, terminal approve/reject is zero-write with a clear blocker, and the governed return/
  correction/review path creates a new complete cycle without changing cycle one.
- Persist pre-007O/pre-007Q approved and rejected register rows with `{}` source JSON; list/detail
  responses remain actor-scoped, standard-envelope, and null-safe with no live reconstruction.
- Rename borrower, requester, every approver, and communication actors between routing/actions and
  terminal generation; new formal rows retain the routed/action-time identities and timestamps.
- Malformed current packages remain nondisclosing/zero-write, while legacy-compatible facts never
  widen permission, case scope, document authority, counts, or pagination.

## Evidence Required

Backend RED/GREEN output using explicit legacy row fixtures, focused M05 history/remediation tests,
and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Schema evolution cannot erase valid approval history or crash formal register reads.
- Missing historical terminal facts are never invented from live data.
- Formal approver identities remain immutable across later user-profile edits.
- All configured gates pass.

