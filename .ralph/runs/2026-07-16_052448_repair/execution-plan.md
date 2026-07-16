# Execution Plan — 009A SAP Customer Code Request

1. Diagnose the repair entry, confirm permissions/protected paths, and inspect only the existing application, approval, member, document, encryption, audit, workflow, and permission seams needed by 009A.
2. Establish one deep finance-owned interface for request creation: authenticated actor, canonical loan-application id, and persisted Senior Manager Finance assignee id in; replay-safe restricted request projection out.
3. TDD in vertical cycles through the public service/API seam: first terminal-sanction success (RED/GREEN), then canonical snapshot/workbook/security evidence, denial and validation rollback, replay, and PostgreSQL race behavior. Save every required RED/GREEN and race log.
4. Add the finance models/migration, permission seed, URL/view/envelope contract, restricted Annexure-I storage, encrypted sensitive fields, and atomic audit/workflow evidence without implementing send, completion, SAP code confirmation, or readiness.
5. Update API contracts and run focused checks, migration sync, full backend coverage, and frontend gates. Inspect the workbook programmatically and save sanitized evidence.
6. Review against the slice and source digest, enforce diff/protected-path limits, sharpen the next one or two Not Started slices only from already-opened Epic 009 material, then update slice/state/progress/handoff and all required run artifacts.

Repair diagnosis: normal run `2026-07-16_052447_normal_run` stopped at preflight (`No slice files found`) before creating a worktree or implementation; this repair starts 009A from the clean staging baseline.
