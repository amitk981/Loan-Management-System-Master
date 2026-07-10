# Execution Plan

Selected slice: `005I4-application-detail-backend-state-hardening`

## Scope and constraints

- Change the staff Application Detail frontend, its focused tests, and the narrow existing staff
  detail serializer. Inspection proved the §19.3 detail DTO currently omits `assigned_owner` and
  `available_actions`, even though the list DTO owns the former and §19.3/§44 own the latter. Add
  only those metadata fields; do not add future workflow state.
- Preserve the existing prototype components, classes, layout, colours, typography, and tabs.
- Remove frontend-owned future workflow facts rather than implementing documentation, sanction,
  security, SAP, or disbursement workflows early.
- Keep document badge counts as a direct presentation of checklist rows only.

## TDD tracer bullets

1. Add a staff detail API regression proving `assigned_owner` comes from the persisted receiver/
   creator and `available_actions` is an object-shaped list containing implemented, authorized
   application actions only. Implement the narrow serializer/view projection and update the working
   contract.
2. Replace the `initialData` / `initialActiveTab` production bypass with a production loader plus
   render-only view boundary. Mock the application HTTP service in tests and cover loading, success,
   and error rendering through that same loader/view seam. Save the failing and passing focused-test
   output under `evidence/terminal-logs/`.
3. Add a submitted-state regression with a backend owner name that conflicts with every former
   inferred department. Prove that exact owner is rendered and that fixed dates/completion claims,
   synthetic future fields, and payment-readiness text are absent; implement the smallest correction.
4. Add a later-stage regression with a second conflicting backend owner and object-shaped
   `available_actions`. Prove no owner inference, SAP/documentation/disbursement synthesis, or
   payment CTA survives; implement neutral existing-pattern output for facts the backend does not own.
5. Preserve and move the `LO00000035`, rejection-note, empty witness, and selected nominee
   regressions onto the HTTP loader/view seam. Assert all selected-nominee metadata-only fields are
   rendered while PAN/Aadhaar labels, tokens, hashes, and reveal controls remain absent.

## Verification and evidence

- Run the focused Application Detail test after every red/green cycle.
- Run frontend lint, typecheck, full tests, and build.
- Run backend `manage.py check`, full tests, migration drift check, and coverage with
  `/Users/amitkallapa/LMS/.ralph/venv/bin/python`, even if production backend files remain unchanged.
- Save self-contained submitted and later-stage visual evidence using the available repository
  evidence mechanism; document any browser-runtime limitation honestly.
- Run the implementation review required by the implementation workflow, then record findings and
  traceability in the review packet.
- Save `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, `final-summary.md`, and gate
  logs; update the slice status, Epic 005 digest, Ralph progress/state, and handoff only after gates
  pass.
- Sharpen the next one or two Not Started slices using only their existing source-backed digests and
  source sections already opened for those slices.
