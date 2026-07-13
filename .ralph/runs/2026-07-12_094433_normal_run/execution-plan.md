# Execution Plan

Selected slice: 006Y3-member-registry-and-identity-change-approval-closure

1. Add public-interface backend tests for the Member Registry seam, exact permission denials,
   duplicate protected identities, complete masked history, validation, and the two-actor
   optimistic identity-change request/approval lifecycle. Save a focused failing run first.
2. Introduce the registry module and persisted identity-change request with one migration; keep
   HTTP views as envelope adapters and route legacy reverification through the governed request.
3. Add API/action parity and zero-write denial tests, then implement only the behavior required to
   turn each red case green. Save duplicate-boundary and masked-history evidence.
4. Replace the reason-only staff form with existing modal/action composition, complete both source
   field variants, add request/approval API wiring, canonical refetches, and mounted routed tests.
5. Add the declared trusted-browser contract and encoded baselines where locally feasible; collect
   locally without treating sandbox Chromium launch denial as product failure.
6. Run focused and full backend/frontend gates, record HTTP/matrix evidence, update API contracts,
   assumptions, run artifacts, state/progress/handoff/slice status, and sharpen the next two queued
   slices using only already-opened Epic 004 material.
