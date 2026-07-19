# Slice 012C: Export Masking and Permission Checks

## Status
Not Started

## Parent Epic
Epic 012: Reports, Exports, Hardening, Regression, and UAT Readiness
Epic file: `docs/epics/012-reports-exports-hardening-uat.md`

## Goal
Make every 012B export fail closed on report, object, column, and sensitivity authority, with
default masking, reason-gated sensitive export, expiring scoped downloads, and complete audit.

## User Value
Users receive only the columns they are authorised to export, while compliance can prove who
requested and downloaded sensitive information and why.

## Depends On
- 012B

## Runtime Capabilities

- `none`

## Source References
- `docs/source/security-privacy.md` sections 14.3-14.4, 24, and 32
- `docs/source/product-requirements.md` sections 11.31-11.32
- `docs/source/auth-permissions.md` sections 11.1, 12.13, 19, and 33.3
- `docs/source/codebase-design.md` section 33.3
- `docs/source/test-plan.md` sections 18.2-18.5 and 22.2 (`EXP-001`-`EXP-010`)
- `docs/source/api-contracts.md` sections 40.7-40.8
- `docs/working/digests/epic-012-reports-exports-hardening-uat.md` section 012C

## Prototype Reference
- sfpcl-lms/src/pages/reports/ReportsMIS.tsx
- sfpcl-lms/src/pages/registers/RegistersHub.tsx
- sfpcl-lms/src/pages/Dashboard.tsx

## Screens Involved
None directly.

## Frontend Scope
None for this slice, except updating frontend documentation or fixtures if required by tests.

## Backend/API Scope
- Add a central export policy/classification decision used both before queueing and before file
  creation/download. Report read, `reports.export`, object/team scope, allowed columns, report
  classification, and sensitive-export authority are evaluated independently.
- Mask PAN, Aadhaar, bank account, cheque, and BO-account fields by default using established
  masking helpers. Omit forbidden columns; never copy raw values into job metadata, URL, logs, or
  audit payloads.
- An unmasked permitted-column export requires separate sensitive-export authority and a
  nonblank reason; audit the authority, reason, classification, actor snapshot, job, and outcome.
  Require the source-defined `reports.export_sensitive` permission. Its role grants remain
  unresolved, so grant it to no additional role unless an authoritative mapping lands; unknown
  role combinations deny rather than broadening `reports.export`.
- Bind status/download access to the requesting actor's permitted scope (or an explicitly
  authorised auditor/admin policy), and re-check authority at download time. Expired,
  cross-user, cross-team, or revoked access is denied.
- Rate-limit excessive export attempts using existing infrastructure when present and preserve
  a security/audit signal for denials.

## Database/Model Impact
Extend the 012B job only with classification, requested/permitted column policy, masked/sensitive
decision, reason reference, and authority snapshot if needed. Store no plaintext sensitive data.

## API Contracts
Document optional requested columns and sensitive reason only if required by the implementation;
preserve 40.7-40.8 response compatibility and standard 403/410 error shapes.

## Permissions
Read permission does not imply export; `reports.export` does not imply
`reports.export_sensitive`. Audit-log export is Restricted, recovery is Critical Restricted, and
bulk KYC is disabled or requires the highest approved authority. The permission code is binding;
its unresolved role grants default deny.

## Audit Requirements
Audit request, denied request, sensitive grant, generation outcome, download, expired/revoked
download, and unusual attempt rate through the immutable recorder. Sanitise all before/after and
reason fields; never audit raw exported rows.

## Validation Rules
- Policy is evaluated against authoritative server-side roles/scope, never client claims.
- Masking is per field and format and cannot be reversed from displayed/exported output.
- Generated files contain only permitted columns; signed URL possession alone cannot grant
  access after scope/expiry/revocation checks.

## Test Cases
- Implement `EXP-001` through `EXP-010`, including filter equivalence, retention/expiry,
  generated-by/time metadata, audit-export restriction, and large async export.
- `SEC-PII-009` and format-parameterised tests prove all five sensitive field families are masked
  without authority and revealed only with authority + reason; blank/missing reason is denied.
- Cross-user/team/object, revoked permission, guessed job ID, expired link, forbidden column,
  bulk-KYC, and excessive-attempt negative tests.
- Reverse-consumer tests prove ordinary report reads, existing reveal/download audit, 012B retry,
  and audit-log sanitisation remain intact.

## Visual Acceptance Criteria
None.

## Evidence Required
RED/GREEN and full-gate output; permission/classification matrix; parsed masked and authorised
files for each format; denial/expiry examples; immutable sanitised audit rows; no-secret scan.

## Non-Goals
Frontend wiring, a redesign of ordinary sensitive reveal, new report definitions, live sharing,
or granting unknown roles/permissions access.

## Risk Level
High

## Acceptance Criteria
- Every export and download is independently authorised, scoped, classified, expiring, and
  audited; unknown policy denies.
- Sensitive fields are masked by default and unmasked only for permitted columns with separate
  authority and a recorded reason.
- Export files, jobs, logs, URLs, and audit metadata contain no unauthorised raw sensitive data.
- Frontend wiring and changes to general sensitive-reveal policy remain out of scope.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Database rules followed, if needed
- [ ] Permissions tested, if needed
- [ ] Audit events tested, if needed
- [ ] Visual evidence saved, if frontend
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Substantive unresolved risk or decision recorded only if needed
- [ ] Commit created only after passing gates
