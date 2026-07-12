# Review Packet: 2026-07-13_014006_normal_run

## Result
Ready for independent validation

## Slice
006Z8-portal-limit-provenance-module-and-interaction-closure

## Traceability

- Functional BR-003..007 require verified active-member evidence: credit recalculates using the
  persisted calculation date and compares the exact result id/snapshot, verified by the next-day API
  regression in `test_portal_member_api.py`.
- API §6-§8/§22-§24 require redacted envelope-backed borrower data: the portal API returns only the
  ten documented projection fields and tests exclude member, authority, result, evidence, verifier,
  and staff-action facts.
- Codebase design §22.1/§26.1-§27.1/§42 moves policy behind a deep module: `project_borrower_limit`
  owns all selection, resolution, arithmetic, and advisory decisions; the adapter boundary test
  rejects their return to `members.portal_services`.
- Frontend rules preserve the existing cards/advisory/review row and formatter. Mounted Vitest and
  the four-case Playwright spec cover available/unavailable/advisory/review rendering.

## Recommended Next Action

Run independent Ralph validation, including both trusted browser executions; commit only if green.
