# Review Packet

## Standards

Fail. The independent standards review found six hard violations: client-calculated server-owned
state, swallowed API failures, prohibited hub/card/table/modal redesigns, and missing screenshot
evidence. The source-string mock regression is too weak to prove removal of inline business rules.

## Spec

Fail. The independent spec review found seven material gaps. Most critically, download controls
are synthesized from document ids rather than a server-issued latest-current capability, and the
UI combines three non-atomic responses instead of consuming one locked projection. Required
generation, verification, security, final-approval, replay/conflict, and role-turn behavior is
absent; tri-party/cancelled-cheque coverage and required behavioral tests are also missing.

## Gate evidence

- Frontend lint, typecheck, 306 tests, and production build: pass.
- Django check and migration drift: pass.
- Backend: 900 tests pass (46 skipped); 92% coverage against 85% floor.
- Visual acceptance: not collected; browser-control skill reported no browser available.

Conclusion: tooling passes do not satisfy the slice. Do not commit or merge this working tree.

