# Risk Assessment

Selected slice: 003IA-notifications-center-ui-wiring

Risk level: Medium

## Why Medium
- Adds a new persisted notification inbox model and one migration.
- Adds protected current-user APIs with object-level recipient filtering and read-state mutation.
- Changes staff UI data sources for Notifications Center and My Profile.

## Controls Applied
- TDD red/green evidence saved for backend notification API and frontend notification/profile wiring.
- Object-level recipient filtering tested for direct user, role, team, and other-user exclusions.
- Mark-read uses optimistic `read_state_version`, persists read state, and audits the mutation.
- Notification APIs use a narrow `communications.notification.read` permission instead of broad
  communication-send, dashboard, report, or frontend-only permissions.
- Preserved deliberately permission-neutral `it_head` and `sales_team_user` seed behavior.
- Real provider delivery, borrower/member portal notifications, snooze/dismiss rules, and dashboard
  task mutation remain out of scope.

## Residual Risk
- Role/team notifications currently share one read state row if manually created; per-user read state
  for broadcast notifications is recorded as an A-026 follow-up pending source confirmation.
- Browser screenshots could not be captured because localhost binding and browser/renderer launch are
  blocked by sandbox permissions. Logs record the exact blockers; gates and render tests passed.

Manual review required: normal Ralph review only.
