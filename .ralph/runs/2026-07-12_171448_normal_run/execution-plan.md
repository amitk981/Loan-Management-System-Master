# Execution Plan

Selected slice: `006Y9-member-form-real-session-closure`

1. Inspect the routed Member Directory/Profile containers, staff session helpers, member API
   adapters, seeded browser actors, and the 006Y5/006Y7 governance contracts. Keep the backend
   Registry and approved frontend composition unchanged unless a failing boundary test proves a
   reachability defect.
2. Add failing-first mounted interaction coverage that exercises the production containers through
   authenticated HTTP (without mocking member API wrappers): complete individual and institution
   request bodies, exactly one mutation and canonical detail refetch, masked canonical readback,
   and one-call authoritative 400/403/409/requester-checker errors.
3. Add the declared `member-governance-variants.e2e.spec.ts` trusted-browser flow. Begin at real
   staff login, create uniquely identified individual and institution variants, reload masked
   canonical detail, request a protected correction, prove requester denial, switch through the
   visible sign-out boundary, and approve as the separate checker. Produce only the four declared
   masked screenshots.
4. Run focused red/green frontend tests and Playwright collection, then frontend build, typecheck,
   lint, and full tests. Run backend check, migration sync, and full coverage with the mandated
   Ralph Python interpreter. Save terminal logs and exact masked HTTP evidence; do not treat a
   sandbox Chromium launch denial as a product failure.
5. Review scope/risk, save changed-files and review packet, update API/digest documentation only if
   the executable contract reveals a material mismatch, sharpen the next eligible slices using
   already-opened source extracts, and update slice status, state, progress, and handoff.
