# Slice 003IA: Notifications Center UI Wiring

## Status
Not Started

## Parent Epic
Epic 003: Audit, Documents, Config, and Dashboard Foundation
Epic file: `docs/epics/003-audit-documents-config-foundation.md`

## Goal
Wire the staff Notifications and Alerts Center (screen S04) and the staff My Profile page to real backend data, so notifications produced by the 003I notification adapter are visible in the UI instead of mock data.

## User Value
Staff see their real pending alerts and notifications in the shell they already know, and the notification foundation from 003I becomes reachable in the product.

## Depends On
- 003I

## Source References
- docs/source/screen-spec.md section 5.8 (notification pattern) and screen S04
- docs/source/api-contracts.md section 39 (communication APIs) and section 43 (dashboard APIs) for endpoint conventions
- docs/source/information-architecture.md (navigation placement)
- docs/source/content-spec.md (notification wording)

## Prototype Reference
- sfpcl-lms/src/pages/notifications/NotificationsCenter.tsx
- sfpcl-lms/src/pages/profile/MyProfile.tsx

## Concrete Requirements
1. Backend: notification list and mark-read endpoints for the current user, following the standard envelope, pagination (api-contracts §8.1), and naming conventions; record contracts in `docs/working/API_CONTRACTS.md`.
2. Frontend: replace mock notification data in `NotificationsCenter.tsx` with the real API, preserving the existing layout per `docs/working/FRONTEND_DESIGN_RULES.md` (no new styling or components).
3. Frontend: wire `MyProfile.tsx` to the current-user API from 002D (read-only display; password/session management stays out of scope).
4. Cover loading, empty, error, and unauthorized states using existing patterns.

## Test Cases
- Notification list returns only the current user's notifications (object-level permission test).
- Mark-read is persisted and audited where required.
- Frontend states: populated, empty, error.

## Out of Scope
Real email/SMS delivery (adapter stays shell), member-portal notifications (slice 011NA), reminder generation (010J).

## Risk Level
Medium

## Acceptance Criteria
- Notifications Center shows backend data end to end; no mock data remains on this screen.
- My Profile reflects the real current user.
- All gates pass; screenshots saved as visual evidence.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated
- [ ] Permissions tested
- [ ] Visual evidence saved
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
