# Execution Plan

Selected slice: 006Z-produce-supply-history-persistence

1. Establish the source-backed contract and current seams.
   - Use data-model §11.6, functional-spec BR-003–BR-007/M02-FR-004/M04-FR-004,
     API contract §16, the Epic 006 digest, and the existing 006A eligibility and 005FB portal
     boundaries.
   - Reuse existing member resource actions, optimistic `version` handling, audit projections,
     member object access, portal-account own scope, and frontend profile refetch patterns.
2. TDD the persistence and staff API tracer bullet.
   - Add one failing API test for staff capture through the public member endpoint; save RED.
   - Implement the non-destructive `produce_supply_records` migration/model, serialization,
     narrow capture permission/action, validation, audit/history evidence, URL, and view; save GREEN.
3. TDD verification and eligibility integration incrementally.
   - Add failing tests one behavior at a time for maker-checker denial, permission denial, stale
     version rejection with zero side effects, verified/unverified/absent supply history, and
     continuous financial-year evaluation.
   - Implement resource verification with immutable verifier evidence and make the existing
     eligibility module derive its active-member result from persisted verified supply records
     plus the existing source-backed service-availed fact.
4. TDD read contracts and frontend wiring.
   - Add API tests for staff list/detail authority and portal own-only read projection.
   - Replace the portal shell response with persisted records and summary; expose the same facts
     in the canonical staff member-profile response.
   - Update the existing portal supply view and Member Profile/Borrower 360 supply panel using
     only established tables, badges, alerts, forms/modals, and canonical refetch patterns.
   - Add focused frontend service/component/container tests for empty, error, read, capture,
     verify, authority, and refetch behavior.
5. Contract, evidence, and gates.
   - Update API_CONTRACTS, Epic 006 digest, and resolve assumption A-043 without changing source.
   - Run focused red/green commands with the mandated venv, then backend check, migration sync,
     full backend coverage, frontend typecheck/lint/tests/build, and any declared browser contract.
   - Save terminal logs, API examples, review/risk/changed-file/final artifacts; sharpen the next
     one or two Not Started slices from already-opened source material; update slice status,
     progress, state, and handoff only after gates pass.
