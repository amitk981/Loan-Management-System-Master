# Risk Assessment

Risk level: High

- Selected slice: 008M3-documentation-workspace-executable-action-closure
- Mode: repair
- Standing approval: applies; no revocation found.

## Material Risks and Controls

- **Authorization/action drift:** workspace actions previously could be advertised while their owner
  rejected them. Projection now calls owner decisions over current locked facts, and execution
  reconstructs that same current command before dispatch.
- **Object-identity injection:** canonical application, item, document, party, template, bank, and
  security identifiers remain private. The public token is an HMAC of actor, application, checklist
  snapshot, stable action key, and private command; callers cannot replace a `fixed_payload`.
- **Replay/cross-scope disclosure:** unknown, stale, modified, cross-user, and cross-application
  tokens return the same 404 and tests assert zero writes.
- **Regulated workflow side effects:** upload, signatures, stamp/notary, S35, mismatch, bank,
  security, verification, generation, and completion dispatch through existing owner modules so
  their permission, audit, workflow, and state checks remain authoritative.
- **File upload boundary:** the client sends the selected `File` with browser-owned multipart
  framing; the server accepts only declared fields and hands storage/audit to the existing document
  boundary.
- **UI action loss:** both workspace surfaces render every stable sibling action, with Download
  independent. Tests cover multi-action rows, rejection retention, and exactly one success refetch.
- **Browser evidence:** local Chromium was denied macOS services before page creation. Collection
  passes, screenshots were not fabricated, and the orchestrator's twice-run real-browser gate is the
  final acceptance control.

## Residual Risk

The process coordinator is intentionally broad in this behavioral closure. Sharpened slice 008M4
owns the structural deep-module cleanup while preserving this public contract. Residual browser
layout/interaction risk is accepted only subject to independent browser validation.
