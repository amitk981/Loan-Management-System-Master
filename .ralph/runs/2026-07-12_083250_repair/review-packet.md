# Review Packet: 2026-07-12_083250_repair

## Result
Ready for independent validation

## Slice
006Y2-member-form-and-witness-capture-ui-wiring

## Outcome

- Member Directory exposes registration only with `members.member.create`; individual and
  institution payload variants use the governed POST contract.
- Member Profile exposes edit/reverification only from the selected resource's six-field actions.
  PATCH/reverification send the current version; verified identity is masked/read-only; success
  refetches canonical detail; backend validation/stale messages remain authoritative.
- Application Detail replaces the placeholder with application-scoped witness GET/POST wiring,
  masked identity, immutable verification-time folio/shareholding evidence, empty/error/forbidden
  states, and canonical list refresh after capture.

## Traceability

- The source screen spec S05/S06 requires staff member registration/profile management; the code
  composes the existing directory/profile cards and fields; verified by
  `MemberGovernanceForm.test.tsx`, `MemberProfile.test.tsx`, and the browser contract.
- API §13 and 006Y require versioned PATCH plus reasoned verified-identity correction; the code sends
  exact URLs/bodies and consumes resource actions; verified by the member API/form tests.
- Data model §10.5 and screen S09 require application-scoped shareholder witness evidence; the code
  uses 004E2 GET/POST and renders canonical immutable evidence; verified by
  `applicationIntakeApi.test.ts`, existing backend witness tests, and the browser contract.
- Auth permissions require narrow member/witness rights; the deterministic finance role contains
  only the required additions and the zero-permission browser actor sees no member route.

## Validation

- Frontend: build, typecheck, ESLint, and 171 tests passed.
- Backend: Django check and migration sync passed; 411 tests passed, five expected PostgreSQL skips,
  94% coverage (85% floor).
- Browser: spec collection passed (one test). Local Chromium launch was sandbox-denied; independent
  trusted acceptance runs twice and must emit all five declared screenshots.
- Protected files were not modified; no dependency or migration was added.

## Recommended Next Action
Run independent Ralph validation and trusted browser acceptance, then perform the due architecture review.
