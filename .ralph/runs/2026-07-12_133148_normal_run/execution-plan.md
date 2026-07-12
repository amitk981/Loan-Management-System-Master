# Execution Plan

Selected slice: `006Y5-member-registry-governance-and-form-contract-closure`

1. Inspect the existing member module, HTTP adapters, permission/object-access helpers, identity-change workflow, models/migrations, frontend member form, API client, and focused tests. Confirm the exact public surface and current §13.2 omissions without widening the slice.
2. Add one failing public-module test at a time for the registry read/create/update/request/approve permission and object-access matrix, then move authority and governed behavior behind `MemberRegistry` while keeping views as translation adapters.
3. Add failing duplicate-request/approval tests, including the PostgreSQL race contract where supported, then make request-time and approval-transaction duplicate checks translate uniqueness races to standard field errors with atomic zero-evidence rollback.
4. Add a failing requester-with-checker-permission action/write parity test and stale/non-pending/object-denied zero-evidence cases, then centralize approval evaluation so projection and write return the same reason.
5. Add failing mounted frontend tests for complete individual and institution §13.2 payloads and canonical refetch/error behavior, then extend the existing modal and API types using only established visual patterns.
6. Save red and green logs plus HTTP/masked examples in the run evidence folder. Run focused checks, then all configured backend/frontend gates with the mandated backend interpreter.
7. Review the diff for protected paths and slice limits; write changed-files, risk assessment, review packet, final summary, update API/digest/assumptions only where warranted, sharpen the next one or two Not Started slices from already-open sources, and mark slice/state/progress/handoff complete only after gates pass.
