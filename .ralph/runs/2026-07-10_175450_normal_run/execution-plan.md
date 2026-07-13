# Execution Plan

Selected slice: 006D2C-loan-limit-concurrency-and-boundary-regression

## Scope and constraints

- Add regression tests only unless the first failing test demonstrates a production defect required by this slice.
- Exercise the public `LoanLimitCalculator.calculate_for_application(...)` interface under competing, independent database transactions; retain the existing fast lock-call diagnostic.
- Strengthen the static import/module boundary without changing formulas, APIs, persistence, permissions, rerun behavior, audit payloads, or response contracts.
- Use the orchestrator-managed backend interpreter for every Django/test/coverage command.
- Do not modify frontend, protected paths, or source documents.

## TDD sequence

1. Inspect the current calculator, assessment model, test factories, PostgreSQL integration settings, and boundary regression helper. Confirm the exact public seam and existing evidence projections.
2. Add one boundary fixture regression for package-level/aliased/private concrete-model bypasses and required public imports, run it red, and save the failing output under `evidence/terminal-logs/`.
3. Make the minimum boundary-helper/test-fixture change needed for green. Replace exact `AppraisalWorkflow` method equality with required-method subset coverage and prove harmless extra public methods remain allowed.
4. Add one public-interface competing-valid transaction regression using independent connections plus deterministic synchronization. Run it red and save backend/ordering output. Make only the minimum production/test-harness correction required for green.
5. Add the competing valid/invalid regression, verifying the valid snapshot/UUID and success-evidence counts survive and the invalid attempt adds no success evidence. Save focused green logs.
6. Run the existing calculator characterization, rollback, rerun, HTTP, and boundary suites; then run all Ralph quality gates with the mandated backend interpreter.

## Observable assertions

- Two successful competing reruns leave exactly one assessment row and one stable assessment UUID.
- The final row is one internally consistent complete snapshot from one calculation; audit/workflow success evidence agrees with successful commits and the final audit projection agrees with the row.
- A competing invalid attempt cannot overwrite the valid committed snapshot or create success audit/workflow evidence.
- Both `ast.Import` and `ast.ImportFrom` bypass shapes, including package aliases and private concrete imports, are rejected outside owning modules.
- Production consumers positively import the public calculator/appraisal seams; unrelated extra public workflow methods do not fail the boundary.

## Completion artifacts

- Red/green logs identifying database vendor and deterministic transaction ordering.
- Boundary fixture output and standard gate logs.
- `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, and `final-summary.md`.
- Updated slice status, Ralph state/progress, handoff, epic digest, and sharpened next one or two Not Started slices using only already-opened source material.
