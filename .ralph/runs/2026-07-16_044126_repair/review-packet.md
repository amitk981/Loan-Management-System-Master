# Review Packet: 2026-07-16_044126_repair

## Result

Ready for independent validation.

## Slice

008M2-documentation-workspace-contract-and-visual-closure

## Demonstrated failure and repair

The external browser reached real Django and received `409` after clicking a rendered `Record
stamp` action on a completed Term Sheet. Terminal checklist evidence correctly prevented the
mutation, but the staff workspace had advertised the action from actor permission alone.

`_item_actions` now projects signature/stamp/notary actions only while the item is pending. The
browser asserts the completed row has no `Record stamp`, posts the exact retained completion facts
and receives replay-safe `200`, posts changed facts and receives `409`, and verifies restricted
content remains `404`.

## Traceability

- The slice says every rendered action must work through its production endpoint and that terminal
  status grants no action (requirements 3, 4, and 7).
- The code now gates evidence mutations on the same pending checklist state used by the completion
  owner and preserves all pending-item actions.
- `test_staff_workspace_is_one_redacted_action_projection` proves completed Term Sheet actions are
  empty for the exact Compliance permission matrix; the adjacent action-family test proves pending
  signature/stamp/notary actions remain present.
- The trusted browser spec proves the real authenticated Django replay/conflict/restricted boundary.

## Validation

- Frontend: build, typecheck, lint, 36 files / 319 tests — PASS.
- Backend: check, migration drift, full suite plus temporary TDD regression (916 executions),
  48 expected skips, 91% coverage — PASS; final folded focused regression — PASS.
- Browser: collection PASS; local launch sandbox-blocked before page creation.
- Integrity: protected paths clean, `git diff --check` PASS, 1,998/2,000-line diff PASS.
- Queue readiness: 009A and 009B were inspected and are already concrete, source-cited,
  dependency-ordered implementation slices; no diff-expanding rewrite was needed.

## Recommended next action

Run `e2e/staff-documentation-workspace.e2e.spec.ts` twice outside the sandbox, verify the four
declared non-empty PNGs, then commit/merge only if independent validation is fully green.
