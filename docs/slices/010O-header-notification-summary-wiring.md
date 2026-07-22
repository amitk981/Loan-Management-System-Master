# Slice 010O: Header Notification Summary Wiring

## Status
Complete

## Parent Epic
Epic 003: Audit, Documents, Config Foundation (notifications continuation)
Epic file: `docs/epics/003-audit-documents-config-foundation.md`

Note: filename-scheduled after 010N because 010N removes Header.tsx's mock search paths first; this slice removes the header's remaining mock surface. The capability is Epic 003 scope debt — the Notifications Center is API-backed (003IA) but the header dropdown still renders hard-coded rows (PRODUCTION_COMPLETION_BLUEPRINT.md §6.3).

## Goal
Wire the header notification dropdown to the real notifications API and remove the final mock reads from `Header.tsx`.

## User Value
The bell icon shows real unread state; staff stop seeing phantom notifications that no API produced.

## Depends On
- 010N

## Runtime Capabilities

- `localhost-e2e-server`

## Trusted Browser Acceptance

- Spec: `e2e/header-notifications.e2e.spec.ts`
- Screenshot: `header-notifications-populated.png`
- Screenshot: `header-notifications-empty.png`
- Screenshot: `header-notifications-error.png`

## Source References
- docs/source/screen-spec.md S04 notifications and header shell
- docs/slices/003IA-notifications-center-ui-wiring.md (list contract, mark-read, 409 STALE_WRITE)
- docs/slices/003IA2-notification-mark-read-stale-write-hardening.md
- `docs/working/digests/epic-010-servicing-repayments-interest-monitoring.md` §010M–010O

## Prototype Reference
- sfpcl-lms/src/components/layout/Header.tsx

## Concrete Requirements
1. Header dropdown fetches a bounded summary from the existing `GET /api/v1/notifications/` contract (unread count + latest N); no new endpoint unless the contract genuinely lacks a summary shape — if so, extend the contract in API_CONTRACTS.md first.
2. Mark-read from the dropdown reuses the versioned mark-read endpoint with 003IA2 stale-write handling; "view all" routes to the Notifications Center.
3. Remove the hard-coded notification rows and the `mockData` import from `Header.tsx` (search usage already removed by 010N). This slice owns the final assertion that `Header.tsx` has no mock reads.
4. Loading, empty, error, unauthorized states in the dropdown; existing patterns only; unread badge reflects backend count.

## Owned Mock Removals
- `src/components/layout/Header.tsx` — final owner: no `mockData` import or inline notification fixtures remain.

## Test Cases
- Dropdown renders API rows and real unread count; empty and error states covered.
- Mark-read asserts exact URL/body and handles 409 refresh.
- Regression: `Header.tsx` does not import `src/data/mockData.ts`.

## Out of Scope
Global search (010N), Notifications Center behaviour (003IA), portal notifications (011NA), notification generation rules (owning module slices).

## Evidence Required
Saved RED/GREEN service/component output for populated, empty, error, unauthorized, mark-read, and
409 refresh behavior; exact request/response assertions and final mock-removal proof; all three
trusted-browser screenshots from two passing contract runs; focused notification regressions and full gates.

## Risk Level
Low

## Acceptance Criteria
- Header notification surface is backend truth end to end; header mock surface is zero.
- All gates pass; screenshots of populated, empty, and error dropdown states saved.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] Permissions tested
- [ ] Visual evidence saved
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Ralph owns mechanical bookkeeping; record only substantive unresolved risks/decisions in `review-packet.md` and `HANDOFF` if needed
- [ ] Commit created only after passing gates
