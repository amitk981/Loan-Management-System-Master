# Data Import and Migration Plan

Source baseline: `docs/source/implementation-roadmap.md` sections 10, 20-22, 26, 30-31;
`docs/source/data-model.md` sections 16, 24-31, and 34; `docs/source/api-contracts.md`
sections 39-43 and 45; `docs/source/component-spec.md`; `docs/source/design-system.md`.

This is a planning artifact only. Slice 003L does not add import commands, import staging tables,
background workers, public import APIs, frontend screens, or real data loads.

## Current Implementation Boundary

The platform has implemented foundation tables and APIs for selected R1 areas:

| Area | Implemented foundation | Import planning status |
|---|---|---|
| Users, roles, permissions, teams | Identity catalogue, users, role/team membership, session auth | Eligible for future controlled seed/import planning using source-backed role and permission codes only. |
| Audit logs | Append-only `audit_logs` with `GET /api/v1/audit-logs/` | Migration batches must write audit summaries; existing audit rows must not be updated or deleted by application workflows. |
| Workflow events | Canonical `workflow_events` read API and internal record service | Historical lifecycle imports may create explicit historical events later, but only after owning workflow slices define allowed state semantics. |
| Document files | `document_files` upload metadata, checksum, storage adapter, secure download descriptor | Future document migration can map scanned physical files to storage keys/checksums and sensitivity levels. |
| Loan policy configuration | `loan_policy_configs` plus `version_histories` for loan-policy shell | Future config imports can map approved policy versions, effective dates, and board references. |
| Content templates and communications | `content_templates`, `communications`, no-provider send/list shell | Future imports can load approved template metadata and historical communication records without provider replay. |
| Notifications | Current-user `notifications` inbox and versioned mark-read | Notification-center data is API-backed, but historical communication imports must not become user inbox notifications unless a later slice defines that rule. |
| Dashboard shell | `GET /api/v1/dashboard/` returns role context, zero-count cards, and empty `tasks[]` | Dashboard is API-backed, but task generation and business counts are not implemented yet. |
| Scheduled jobs | Internal `scheduled_jobs` metadata shell | Future async imports or report exports may use job metadata to track batch status; no worker exists yet. |

Current prototype/API status from 003K remains binding:

- Dashboard, Notifications Center, and My Profile are API-backed.
- Task Inbox is still prototype/mock. There is no task inbox API or task generation engine.
- `AuditTimeline` and `DocumentPackModal` remain mock/prototype UI components until dedicated UI
  wiring slices connect them to audit/workflow/document APIs.
- `scheduled_jobs` is internal metadata only. It is not a task inbox, scheduler UI, dashboard task
  generator, notification generator, or report worker.

## Source Data Areas

`implementation-roadmap.md` section 26 says the migration decision must cover existing member
records, shareholdings, existing loans, SAP customer codes, repayment history, interest balances,
documents, security custody records, and compliance evidence.

`data-model.md` section 31 identifies likely source data as:

| Source candidate | Future target areas |
|---|---|
| Existing Excel Loan Register | Loan applications, loan request register entries, loan accounts |
| Member/shareholder records | Members, shareholdings, share certificates |
| Physical KYC files | KYC profiles, KYC documents, document files |
| SAP customer master | SAP customer codes, bank accounts |
| SAP accounting entries | Repayments, accrual entries, interest invoices |
| Physical loan files | Loan documents, document checklists, security packages |
| Manual sanction records | Approval cases, approval actions, sanction decisions, credit sanction register entries |

## Existing Foundation Table Mapping

These implemented areas can be mapped to concrete models/APIs in future import slices:

| Foundation target | Natural key candidates | Required controls |
|---|---|---|
| Users | Email, employee code if added later | Active/inactive mapping, role/team references, no plaintext passwords in import files. |
| Roles and permissions | `role_code`, `permission_code`, `team_code` | Use source catalogue codes; reject unknown permission grants unless a source-backed assumption exists. |
| Document files | Legacy document reference plus checksum/storage key | Validate file presence, size, MIME type if known, SHA-256 checksum, sensitivity, storage provider/key, retention date. |
| Audit logs | Migration batch id plus source event reference | Append only; log summaries and metadata, not raw file payloads or full sensitive values. |
| Workflow events | Entity type, entity id, source event reference | Import only historical facts allowed by owning workflow slices; do not invent transition rules. |
| Loan policy configs | Policy name, version, effective date | Validate effective dates, status mapping, board approval reference where required. |
| Version histories | Versioned entity type/id plus version number | Preserve author/reviewer/approver references where available; otherwise record missing reference as an exception. |
| Content templates | `template_code`, version, audience/language | Validate required fields, variables, approval status, and effective dates. |
| Communications | Related entity, recipient, channel, source message id | Preserve subject/body snapshots without provider replay; mask sensitive addresses in evidence where required. |
| Notifications | Notification id or source alert reference | Do not import communication history as unread inbox items unless a future notification slice defines source-backed rules. |
| Scheduled jobs | Import/export batch id, job type, idempotency key | Track batch metadata only until real workers and admin APIs are implemented. |

## Future Business Target Areas

These are target areas only until owning slices create schema, APIs, permissions, object access,
and tests:

| Target area | Source-backed tables or API groups | Planning note |
|---|---|---|
| Member, KYC, shareholding | `members`, individual/FPC profiles, nominees, witnesses, shareholdings, share certificates, demat accounts, active-member statuses, KYC profiles/documents, bank accounts | Do not invent KYC approval, active-member, nominee, witness, share availability, or default rules in import planning. |
| Applications and appraisal | Loan applications, loan request register entries, application documents, deficiencies, eligibility/loan-limit/risk assessments, appraisal notes, rejection notes | Preserve legacy application references where available; status mapping must be owned by application workflow slices. |
| Approval and sanction | Approval matrix rules, approval cases/actions, sanction decisions, registers, exceptions, general meeting approvals | Historical approvals need actor, authority, timestamp, reason/evidence, and source register references. |
| Loan documentation | Loan documents, document templates, document checklists/items, signature records, stamp duty, notarisation | Store scanned physical evidence through document storage; missing documents become deficiencies or historical exceptions only when owning slices define the path. |
| Securities | Security packages, PoA, SH-4, CDSL pledges, blank-dated cheques, custody events | Custody location mapping is mandatory; sensitive identifiers stay encrypted/masked under later model rules. |
| SAP, disbursement, loan accounts | SAP customer profile requests/codes, loan accounts, terms, disbursements, bank transfers | Existing SAP customer codes must link to members; balances and disbursement state require reconciliation before go-live. |
| Repayments, interest, monitoring | Repayments, allocations, schedules, invoices, accruals, capitalisations, DPD statuses, reminders, MIS reports, portfolio snapshots | Outstanding balances must reconcile with SAP/source; do not invent allocation, DPD, or interest calculations. |
| Default, recovery, closure | Default cases, assessments, extensions, non-payment notes, recovery decisions/actions, loan closures, NOCs, security returns, archive records | Historical recovery and closure evidence must remain auditable and linked to loan accounts. |
| Compliance and reports | Compliance controls/tasks/evidence, Section 186 trackers, NBFC tests, money-lending reviews, stamp-duty compliance, reports/export jobs | Sensitive exports need permission control and audit logging; report outputs must reconcile during UAT. |

## Import Controls

Every future import implementation slice should include these controls before production use:

- Dry-run mode that validates files and reports changes without writing domain records.
- Row-level validation with deterministic line/row identifiers and error summaries.
- Idempotency using natural keys and batch ids so retrying the same file does not duplicate records.
- Source reference preservation using `legacy_reference_number`, `migration_batch_id`,
  `migrated_flag`, `migrated_at`, and `migration_notes` where owning tables add them.
- Reference integrity checks before commit: members before applications, applications before loan
  accounts, loan accounts before repayments/default/closure, documents before document links.
- Atomic commit per safe batch boundary; if a batch spans money, security custody, or documents, the
  owning implementation slice must define transaction boundaries explicitly.
- Rollback/cancel plan for uncommitted or partially validated batches; committed production imports
  should be corrected by auditable reversal/correction records rather than deleting audit evidence.
- Retry plan that distinguishes validation failures, transient storage/job failures, and duplicate
  natural-key submissions.
- Reconciliation reports for member/shareholding counts, SAP customer-code links, balances,
  document links, security custody, and compliance evidence.
- Test-safe synthetic fixtures only. Do not commit real personal, financial, borrower, SAP, bank,
  KYC, or document payload data.

## Validation Categories

Planning should list validation categories without inventing business rules:

| Category | Checks |
|---|---|
| Identity and dedupe | UUID format, legacy business-key uniqueness, duplicate PAN/Aadhaar/bank/account hashes where owning models support hashes. |
| Required fields | Presence of source-required and target-required fields for the target area. |
| Reference integrity | Member/application/loan/document/security/compliance references resolve before commit. |
| Status mapping | Source statuses map to target enums; unmapped statuses produce exceptions, not guessed states. |
| Date and timezone normalization | Dates, timestamps, effective periods, and migrated-at values normalize consistently. |
| Money precision | Amounts parse as decimal strings with target precision; balances reconcile before go-live. |
| Document integrity | Storage key exists, checksum present where required, sensitivity level mapped, retention date present where required. |
| Sensitive fields | PAN, Aadhaar, bank accounts, cheque numbers, BO accounts, KYC/security documents, and sensitive exports follow masking/encryption/reveal rules. |
| Workflow gates | Imported lifecycle states are accepted only where owning workflow slices define legal states and required evidence. |

## Permissions and Operating Model

Future import execution is administrative/high-control work. It should not reuse communication,
dashboard, notification, document-download, or report-export permissions as an import-administration
substitute.

Minimum future permissions to define in source or a dedicated slice:

- Import plan/read access for reviewing batch metadata and validation summaries.
- Dry-run execution.
- Commit execution.
- Rollback/cancel or correction execution.
- Sensitive-data reveal/export during migration review.

Until exact source permission codes exist, import execution must remain unimplemented. This gap is
recorded in `docs/working/ASSUMPTIONS.md`.

## Audit Requirements

Future import slices must create audit records for:

- Import batch created/started.
- Dry-run completed with validation summary.
- Row-level validation failure summary, without raw payloads or full sensitive values.
- Commit started and committed.
- Rollback/cancel/correction.
- Sensitive data reveal or export during migration review.
- Operator role/permission changes for migration administration.

Audit metadata should include batch id, source type, target area, row counts, failure counts,
checksum/file metadata where safe, actor, timestamp, and result. It must not log raw source files,
full PAN/Aadhaar/bank identifiers, full document contents, or unrestricted borrower/financial data.

## Scheduled Job Boundary

`scheduled_jobs` may later track asynchronous import batches or report export jobs with job type,
status, due/started/completed timestamps, related entity, idempotency key, attempts, and error
summary. In the current implementation it is only internal metadata:

- No worker or Celery/Redis execution exists.
- No import job enqueue endpoint exists.
- No dashboard task or notification is generated from `scheduled_jobs`.
- No report export job endpoint exists yet, even though `api-contracts.md` sections 40.7-40.8 define
  future export-job contracts.

## Non-Goals for 003L

- No import staging tables.
- No management command, API endpoint, frontend screen, worker, cron, or scheduled job creation.
- No real source data, no sample borrower data, no production-like financial rows.
- No member, loan, repayment, default, closure, compliance, or report schema changes.
- No change to dashboard task generation, Task Inbox, `AuditTimeline`, or `DocumentPackModal`.

## Follow-Up Slice Candidates

- Import administration permission catalogue and audit event shell.
- Generic import batch metadata model and dry-run summary API.
- Member/KYC/shareholding migration mapping after Epic 004 models exist.
- Loan account, repayment, and SAP reconciliation import planning after finance models exist.
- Document-file migration command after document template/loan-document schemas exist.
- Report export job implementation using `scheduled_jobs` only when real report APIs exist.
