# Risk Assessment

Selected slice: `005B-application-submit-and-status-transition`

Risk level: Medium.

## Risk Drivers
- Backend workflow transition changes loan application lifecycle state from `draft` to `submitted`.
- Adds a non-destructive database migration for submitted actor persistence.
- Writes audit and workflow evidence for a critical application action.
- Sensitive member and bank metadata boundaries must remain intact.

## Controls Applied
- TDD red/green evidence saved under `evidence/terminal-logs/`.
- Submit uses the existing workflow guard foundation for `draft -> submitted`.
- Submit validation is intentionally limited to the selected slice facts: member, positive amount,
  declared purpose, and purpose category. Broader nominee/document gates are recorded in A-036 and
  deferred to document/completeness slices.
- Responses and audits preserve 005A masking boundaries: no PAN, Aadhaar, full bank account number,
  token, or hash values.
- One migration only: optional `submitted_by_user` FK.
- No frontend code or design changes.

## Gate Results
- Backend check: passed.
- Backend focused loan-application tests: 5/5 passed.
- Backend full tests: 243/243 passed.
- Backend migration sync: passed.
- Backend coverage: 96%, above 85% floor.
- Frontend lint: passed.
- Frontend typecheck: passed.
- Frontend tests: 80/80 passed.
- Frontend build: passed.
- `git diff --check`: passed.

## Residual Risk
- The broader source submit endpoint mentions nominee and document placeholder gates. Those are not
  implemented in 005B by slice design and are tracked in A-036 plus sharpened 005D.
- Formal `LO...` reference generation remains nullable through submit and is owned by 005C.
