# Execution Plan

Selected slice: 006Z3-active-member-supply-evidence-boundary-hardening

1. Confirm the source-backed BR-004/BR-007 evidence rules and current 006Z API/model contracts.
2. Add a public `members.modules.active_member_status` test proving legacy active flags cannot
   replace persisted service evidence and only canonical, verified, route-eligible supply rows
   contribute to continuity; save the failing output.
3. Implement the member-owned immutable projection and switch credit plus portal consumers to it,
   removing credit imports of member persistence and private helper tests.
4. Add strict public capture tests incrementally for object/known-field validation, canonical year,
   entity/route and UUID relationships, non-negative decimals, evidence reference, and current
   member version; implement standard 400/403/409 behavior with unchanged evidence cardinality.
5. Exercise maker-checker verification and competing/stale paths, run dependency scans and focused
   green tests, then run every configured backend/frontend quality gate.
6. Save terminal/API/audit/dependency evidence and Ralph review artifacts; update API contracts if
   the capture contract changes, sharpen the next one or two eligible slice files from already-read
   material, and update slice status, state, progress, and handoff only after all gates pass.
