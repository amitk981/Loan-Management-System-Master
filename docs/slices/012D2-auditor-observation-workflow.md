# Slice 012D2: Auditor Observation Workflow

## Status
Complete

## Runtime Capabilities
- `none`

## Parent Epic
Epic 012: Reports, Exports, Hardening, Regression, and UAT Readiness
Epic file: `docs/epics/012-reports-exports-hardening-uat.md`

## Origin
Owner-chat source-coverage audit on 2026-07-19 identified M14-FR-012 observation recording as
unowned; 011O and 012D intentionally provide read-only audit views.

## Goal
Let an authorised Internal Auditor record a governed observation against sampled evidence without
mutating the underlying business record, audit log, workflow event, or version history.

## User Value
Auditors can retain the observation and sampled-evidence reference required by M14-FR-012 while
operational teams remain accountable for their own records and corrections.

## Depends On
- 012D

## Source References
- `docs/source/functional-spec.md` M14-FR-012
- `docs/source/auth-permissions.md` auditor observation/comment guidance and audit permissions
- `docs/source/security-privacy.md` restricted evidence and auditor read-only controls
- `docs/source/data-model.md` compliance evidence, audit logs, workflow events, and version history
- `docs/source/test-plan.md` audit immutability and auditor access cases
- `docs/working/digests/epic-012-reports-exports-hardening-uat.md`

## Prototype Reference
- Existing audit/compliance table, timeline, evidence-link, and status patterns only.

## Screens Involved
None in this slice; 012DA owns visual wiring.

## Frontend Scope
None.

## Backend/API Scope
- Add a dedicated `AuditObservation` owner with create/list/detail actions only. An observation
  references a sampled entity/evidence/audit record by safe identifier but never edits it.
- Freeze creator, audit scope, bounded observation text, evidence references, and created time. No
  comment, response, assignment, severity, status, resolution, closure, update, or delete lifecycle is
  introduced without a separate source-backed owner decision.
- Use restricted signed-download metadata for evidence and sanitise all projections.
- Do not make audit logs editable, grant operational mutation to auditors, or implement remediation.

## Database/Model Impact
One non-destructive migration for immutable observations with immutable source references and bounded
text fields.

## API Contracts
Document observation list/create/detail contracts in `docs/working/API_CONTRACTS.md` with standard
envelopes, errors, filtering, and immutable semantics.

## Permissions
Internal Auditor may create and read observations only within explicit audit scope. Other roles
default-deny unless an existing source-backed audit/compliance read permission applies. No permission
grants business-record mutation or unrestricted evidence download.

## Audit Requirements
Record observation creation, restricted evidence access, and every denial in the immutable central
recorder; sanitise observation/evidence content.

## Validation Rules
- Referenced entity/evidence must exist and be in scope; deleted/foreign/guessed references deny.
- Observation text is bounded and sanitised; caller-supplied lifecycle/classification fields reject.
- Original observations and all underlying audit/business truth remain immutable.

## Test Cases
- RED then GREEN: a scoped auditor samples an authorised record/evidence item and creates one durable
  observation whose creator, scope, text, references, and time cannot change.
- Auditor cannot mutate sampled business records; operational roles cannot forge auditor findings.
- Cross-scope evidence, restricted download, blank observation, injection/sensitive content,
  lifecycle fields, update/delete, and permission negatives.
- Reverse-consumer tests keep 011O and 012D read projections and append-only audit guarantees green.

## Visual Acceptance Criteria
Not applicable (backend only).

## Evidence Required
Saved RED/GREEN output; permission matrix; sanitised API examples; immutable observation and audit
proof; restricted-evidence negatives; reverse-consumer and full gates.

## Risk Level
High

## Acceptance Criteria
- M14-FR-012 observations are durable, scoped, immutable, and separate from source truth.
- Auditor observation authority cannot become operational business mutation authority.
- Required focused, security, reverse-consumer, and full gates pass.

## Done Checklist
- [ ] Execution plan written
- [ ] TDD RED/GREEN evidence saved
- [ ] Model, create/read contracts, permissions, and audit implemented
- [ ] Immutability, scope, sanitisation, and evidence access tested
- [ ] Full gates passed
- [ ] Risk and review evidence completed
- [ ] Commit delegated to the orchestrator after gates
