# Ralph Handoff

## Last Run

2026-07-14_100104_normal_run

## Current Status

007T is complete. S23 consumes the exact backend legacy row with top-level null purpose/risk and
retains the existing unavailable-value detail without reconstruction. S21 action POST, detail,
queue-row, optional sanction-decision, and error outcomes now share the newest queue/detail request
authority, so newer success, denied, malformed, and empty states cannot be overwritten.

The existing 007S browser outputs remain declared, with `sanction-action-filter-race.png` and
`credit-sanction-register-legacy-null.png` added for 007T. Local collection passes; the coding
sandbox hit the expected Chromium Mach-port denial before execution, so the orchestrator owns the
authoritative two runs.

## Validation

Evidence is in `.ralph/runs/2026-07-14_100104_normal_run/evidence/`. Frontend build, typecheck,
lint, and all 293 tests pass. Django check/migration sync and all 722 backend tests pass with 22
expected skips at 93% coverage. The focused backend legacy contract and 47 focused register/
workbench component tests pass; trusted browser collection includes both declared specs.

## Next Run

Run 008B2, then 008B3 before 008C. Both were sharpened to test the legal-document public interface,
exact selector pagination, real DOCX package extraction, parsed PDF content, and the honest real-M05
configuration blocker without reversing dependencies or relabelling renderer fixtures as end-to-end.
