# Slice 007S: Register Pattern and Pagination Order Closure

## Status
Not Started

## Parent Epic
Epic 007: Sanction Approval Workflow and Registers
Epic file: `docs/epics/007-sanction-approval-workflow.md`

## Depends On
- 007R

## Runtime Capabilities

- `localhost-e2e-server`

## Goal

Make strict shared pagination reject every inconsistent page, ensure S21 displays only the latest
filter/page request, and restore S23/S25 to an approved existing table/detail composition while
keeping all source evidence visibly reviewable.

## Source / Review References

- `docs/source/screen-spec.md` S21, S23, and S25
- `docs/source/api-contracts.md` §§6.2, 8.1, 25.3, 25.9, and 25.10
- `docs/source/codebase-design.md` §§23.3-23.5, 26.1-26.3, and 42.3
- `docs/working/FRONTEND_DESIGN_RULES.md`
- `docs/slices/007P-sanction-queue-pagination-and-read-boundary-closure.md`
- `docs/slices/007Q-register-source-fields-and-visual-evidence-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-14_064206_architecture_review`

## Concrete Requirements

1. The shared paginated client must reject under-filled nonempty pages, empty or partially filled
   final pages that contradict `total_count`, impossible page/total/page-count combinations, excess
   rows, and inconsistent navigation flags. The only valid final-page row count is the exact
   remainder (or zero when the collection total is zero).
2. S21 must cancel or generation-guard queue/detail work so a late response for an older filter or
   page can never replace the newest requested rows, total, selection, detail, error, or empty
   state. Preserve explicit sanction/object filters and atomically clear stale data on denial/error.
3. Replace the 007Q four-column grouped register redesign with a composition already present in the
   approved prototype: retain the existing register table/headers for scanability and render the
   selected row's complete source evidence in the existing card/detail pattern used by current loan
   pages. Reuse existing classes/components only; introduce no new styling, table pattern, card,
   colour, typography, or layout rule.
4. Keep every 007Q S23/S25 field, immutable/null semantics, strict object-scoped pagination, and
   no-inferred-download rule. The trusted viewport may scroll to the existing detail composition,
   but the named evidence must be visible inside each captured screenshot.
5. UI tests must use internally valid pagination only; remove the `Page 2 of 1` fixture. Consolidate
   duplicate screenshot-quality analysis behind one test helper without weakening either spec.
6. Move coarse actor/type/status/assignment query shaping, deterministic ordering, and page-query
   mechanics into `approval_case_selector`. The approval engine still owns canonical frozen/read-
   scope validation for every countable row and must not trust stored projection flags; views and
   frontend contracts remain unchanged.

## Trusted Browser Acceptance

- Spec: `e2e/sanction-workbench.e2e.spec.ts`
- Spec: `e2e/approval-register-settings.e2e.spec.ts`
- Spec: `e2e/exception-register-evidence.e2e.spec.ts`
- Screenshot: `sanction-paginated-filtered-queue.png`
- Screenshot: `credit-sanction-register-source-fields.png`
- Screenshot: `exception-register-source-evidence.png`
- Screenshot: `exception-register-document-denied.png`

## Trusted Browser Scenario

Delay an S21 page/filter response, issue a newer filter, then release the old response and prove
the latest queue/total/detail remains authoritative. Open S23/S25 through the production shell,
select the source row, place all restored fields and action/document evidence inside the viewport,
and prove the denied variant contains no download control or opaque rendering artefact.

## Test Cases

- Shared-client table of exact valid and malformed first/middle/final/empty page envelopes.
- Out-of-order S21 list and detail promises across page, filter, denial, malformed, and empty states.
- Register component tests use valid totals/pages and assert the approved table plus selected detail.
- Backend behavioral instrumentation proves the selector excludes irrelevant actor/type/status rows
  before engine validation, while malformed stale-true candidates still create no totals/page holes.
  Delete import/source-spelling assertions when the same dependency rule is publicly proven.
- Trusted specs produce all four reviewable outputs in each independent orchestrator run.

## Run-Ahead Sharpening (007R completion, 2026-07-14)

- Preserve 007R's v2 historical-read contract while moving query mechanics: selector narrowing may
  not drop a canonically valid v2 cycle, expose an unknown/malformed schema, or count a case before
  the engine's schema-aware readability and actor-scope decisions pass.
- S21/S22 stale-response guards must replace `available_actions`, `review_facts`, and immutable
  authority/action history atomically with the newest detail. A late v3 response must not overwrite
  a newer v2 remediation blocker (or vice versa), and nullable legacy `full_name` values must render
  with the existing unavailable-value pattern rather than trigger a live identity lookup.
- The restored S23 detail composition must keep 007R's explicit legacy null/empty fields and frozen
  approver ids/names/times. Pagination, selection, and screenshot fixtures must include one null-safe
  legacy row without fabricating purpose, risk, communication, or approver identity.

## Evidence Required

Frontend/backend RED/GREEN output, validator-work evidence, trusted-browser collection/two-run
outputs, source-field viewport proof, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- No malformed or stale paginated response can masquerade as the current authoritative collection.
- S23/S25 follow the fixed prototype design system and visibly retain every source-required fact.
- All configured gates pass.
