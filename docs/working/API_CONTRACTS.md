# API Contracts

## Closure readiness and financial close (011G)

`GET /api/v1/loan-accounts/{loan_account_id}/closure-readiness/` requires
`closure.readiness.read` plus current Credit Manager, Company Secretary, or governed Auditor object
scope. It is non-mutating and derives principal, interest, charges, total outstanding, unresolved
repayment/SAP/reconciliation evidence, pending recovery, and applicable security-return tasks from
canonical records. Its ordered checks are `principal_paid`,
`interest_paid_or_approved_adjustment`, `charges_paid`, `ledger_reconciled`, `recovery_clear`, and
`security_tasks_identified`. This full-repayment slice does not invent an adjustment/settlement
policy: `interest_adjustment_applied` is false and non-zero interest remains a blocker.

`POST /api/v1/loan-accounts/{loan_account_id}/closure/` requires an `Idempotency-Key`, critical
`closure.loan.close`, and an active Credit Manager or Company Secretary in object scope. It accepts
exactly `closure_type = full_repayment` and bounded safe `closure_notes`; caller-supplied readiness or
balance fields return `400 VALIDATION_ERROR`. Inside one transaction it locks the loan, re-evaluates
all canonical checks, and either returns `409 LOAN_NOT_FULLY_REPAID` with retained safe denial
evidence or creates one immutable financial close.

The close freezes all readiness checks and balances, member/account identity, actor and effective
role, UTC time, type, notes, idempotency/payload digests, audit, workflow event, and loan status
history. It sets the account API status to `closed` as required by source API §36.2, while exposing
`closure_stage = financially_closed` rather than claiming `fully_closed_and_archived`. Three
explicit requirement records are created for NOC, applicable security return, and archive; 011H-J
alone own their controlled completion. Closed loan accounts reject ordinary model/API mutation.
Exact replay returns the original close; changed replay or duplicate/change requests return `409`
without a second close, requirement set, history entry, or success audit.

## NOC issuance and access (011H)

`POST /api/v1/loan-closures/{loan_closure_id}/noc/` requires an `Idempotency-Key`, critical
`closure.noc.issue`, an active Company Secretary or Compliance Team Member, and active membership
in the Compliance Team object scope. It accepts exactly
`document_id`, `delivery_mode = email`, the canonical retained borrower `recipient_email`, and an
active Company Secretary `signatory_user_id`. Certificate facts are never accepted from the caller.
The locked closure must be the retained zero-balance `full_repayment` financial close with a pending
NOC requirement. Recovery/write-off or unsupported closure evidence is not eligible.

The referenced document must be the same application's current-renderer-validated, generated
`noc`/`closure` loan document from an approved effective NOC template, with its generation audit.
The issue freezes borrower, loan account, application reference, disbursed amount, full-repayment
time, issuer/role, governed signatory/role, document provenance, and request digests in one immutable
`NocRecord`. It hands one approved `noc_issued_email` snapshot to the existing communication
dispatcher and retains the resulting queued job before completing only the NOC checklist
requirement. Provider execution remains asynchronous; reads derive `queued`, `sent`, or `failed`
from that retained job and never claim provider success early.

Exact replay returns the same NOC/document/communication/job; changed replay or a second issue is
`409 NOC_ISSUANCE_CONFLICT`. Missing/foreign/stale document, wrong signatory, noncanonical recipient,
ineligible close, and unavailable delivery handoff fail without a NOC or success audit and retain a
safe denial audit. A failed handoff can be retried with the same request without generating another
certificate. Five PostgreSQL racers converge on one issue chain by locking the closure.

`GET /api/v1/loan-closures/{loan_closure_id}/noc/` returns the issued metadata to the owning active
borrower portal account, the Credit Manager who performed the retained close, Compliance-scoped
Company Secretary/Compliance readers, or a governed Auditor. Foreign borrowers and same-role staff
outside those object relationships receive a nondisclosing response. `GET
/api/v1/loan-closures/{loan_closure_id}/noc/download/` applies the same object scope, delegates the
signed descriptor to the document owner, and appends the standard `documents.file.downloaded`
audit without logging certificate contents.

## Security return and CDSL unpledge tracking (011I)

`POST /api/v1/loan-closures/{loan_closure_id}/security-return/` requires an
`Idempotency-Key`, critical `closure.security_return.record`, and either Company Secretary authority
or an authorised Compliance Team Member in active Compliance object scope. The loan must retain the
matching full-repayment financial close. The server derives the security package, applicability, and
SH-4/blank-cheque/PoA/CDSL source identities; caller-declared applicability, a foreign package, or a
foreign source item returns `400 VALIDATION_ERROR` without a return record.

For a closure with no security package, an empty request creates one completed aggregate with four
`not_applicable` items. Otherwise the request accepts the matching `security_package_id`, an
`expected_version`, optional verified restricted `acknowledgement_document_id`, and an `items` list.
Each item names its server-owned `source_item_id` and an outcome. Physical `returned` or `released`
outcomes require recipient, UTC time, and the governed acknowledgement; `pending` requires a reason.
CDSL `completed`/`rejected` results retain matching PSN, verified URF, partial/full mode, pledgor and
pledgee DP timestamps, accepted/rejected DP outcome, auto-unpledge flag, completion time where
accepted, and verified completion evidence. BO account values are projected only as masked last-four
values from the CDSL owner.

The aggregate remains `pending` while any applicable item is pending/rejected or the acknowledgement
is absent. A fresh idempotency key and matching version may advance pending items; returned,
released, completed, and rejected outcomes are terminal. Completion atomically advances only the
security-return closure requirement. Exact replay is zero-write, changed replay is
`409 SECURITY_RETURN_CONFLICT`, and stale versions conflict. Each initial item state and later item
transition, denial, aggregate record, and CDSL result is append-only audited. PostgreSQL closure
locking plus unique aggregate/request constraints converge same-key racers on one result and admit
only one of changed concurrent requests.

## Archive manifest and retention (011J)

`POST /api/v1/loan-closures/{loan_closure_id}/archive/` requires an `Idempotency-Key`,
`closure.archive.create`, an active Company Secretary or Compliance Team Member, and active
Compliance Team object scope. It accepts a physical and/or digital location (at least one is
required) plus optional source-compatible `retention_start_date` and `retention_until_date` fields.
The retained financial-close date is always the retention start; a different caller start or an end
date shorter than the server-calculated eight-calendar-year minimum returns `409 ARCHIVE_CONFLICT`.
An omitted end date receives that server minimum, while a later supplied obligation is preserved.

Creation locks the retained full-repayment closure and requires its completed NOC requirement plus
completed or server-derived-not-applicable security return. It creates one immutable archive record
per loan, completes only the archive requirement, and appends one `fully_closed_and_archived`
workflow event without rewriting the earlier financial-close record or loan status history. Exact
replay returns the same manifest; changed-key, changed-location, or duplicate requests return
`409 ARCHIVE_CONFLICT`. Location correction, certificate/destruction, and all direct model
mutation/deletion are outside this contract. `destruction_eligible` is a read-only date projection,
not destruction authority.

`GET /api/v1/loan-closures/{loan_closure_id}/archive/` returns one scoped manifest. `GET
/api/v1/archive-records/?search=&page=&page_size=` returns a standard paginated searchable manifest;
search matches loan-account number, member legal name, and physical/digital archive location.
Both require `closure.archive.read` and Compliance object scope, or active Internal Auditor
read-only scope. Borrowers do not receive archive locations. Successful detail/search access and
denials are audited; audit payloads record identifiers/counts only and never archive paths or search
text. Archived documents remain behind the existing classified document-download owner and its
download audit.

## Non-Payment Note workflow (011D)

`POST /api/v1/default-cases/{default_case_id}/non-payment-note/` accepts exactly the five fields in
source API §§35.6: required trimmed `reason_for_non_payment`, `intentionality_assessment`
(`intentional`, `non_intentional`, or `unclear`), decimal `outstanding_principal_amount`, decimal
`outstanding_interest_amount`, and required trimmed `recommended_recovery_action`. The authenticated
actor must belong to the Credit Assessment Team and retain `defaults.non_payment_note.create`.
Principal and interest are assertions only: both must equal the locked canonical loan-account
balances. Evidence is inherited from the current default assessment and cannot be caller-substituted.

Creation requires one unpaid, open case whose one-year Extension Note has reached the retained
`expired` transition. It creates/replays one draft, freezes due/grace/extension/assessment/evidence
facts, generates one restricted retained PDF through the document owner, and audits the actor and
snapshot. Unknown fields, malformed/negative amounts, or missing narrative return
`400 VALIDATION_ERROR`; inaccessible identifiers return `404 NOT_FOUND`; premature/cured/closed or
changed replay returns `409 CONFLICT`. Exact replay returns the retained note without writes.

`POST /api/v1/non-payment-notes/{non_payment_note_id}/submit-to-sanction-committee/` accepts an empty
JSON object. The actor must be a Credit Manager with `defaults.non_payment_note.submit`. Submission
rechecks locked case and canonical balances, freezes UTC submission time, moves the default case to
`recovery_decision_pending`, and creates/reuses one approval-owned recovery chain containing the
effective configured Sanction Committee snapshot, the exact `recovery` approval-matrix rule selected
by `condition_code = recommended_recovery_action`, and immutable note facts. Exact replay returns the
retained result without writes; unknown fields are
`400 VALIDATION_ERROR`, missing authority is `403 FORBIDDEN`, inaccessible identifiers are
`404 NOT_FOUND`, and changed/stale state or unavailable/ambiguous committee configuration is
`409 CONFLICT`.

Decision inputs and the generated document are immutable after submission. A changed create request
is accepted only after the linked approval case is explicitly `returned_for_clarification`; that
return is audited, the corrected draft gets a new retained PDF, and later resubmission creates the
next case in the same approval chain. Default-case detail projects the note to authorised Credit,
configured-approver, and Auditor readers. Approval-case detail derives approve/reject/return/abstain
availability from the existing approval owner and its exact permission, assignment, conflict, and
version evidence.

## Recovery Decision approval (011E)

`POST /api/v1/default-cases/{default_case_id}/recovery-decision/` accepts exactly:

```json
{
  "approval_case_id": "uuid",
  "decision": "invoke_sh4",
  "decision_reason": "Approved after reviewing the frozen Non-Payment Note."
}
```

The actor must retain critical permission `recovery.decision.create`, be one of the distinct frozen
required authorities, and have recorded an approved action in that case. The locked approval case
must be the note's recovery case, be terminal `approved`, retain every conflict-free required
approval, and freeze the same action in the Non-Payment Note recommendation, approval reason, and
effective recovery matrix `condition_code`. Missing/pending/rejected/returned/foreign, incomplete,
stale, or mismatched evidence returns `404 NOT_FOUND` or `409 CONFLICT` without a decision.

One immutable decision is retained per default, note, and approval case with the reason, exact matrix
and authority evidence, approver action identities, attributable role code, UTC time, audit row, and
workflow event. Exact replay returns that record without writes; changed replay or a second decision
returns `409 CONFLICT`. Unknown/forged fields, missing reason, or malformed UUIDs return
`400 VALIDATION_ERROR`; missing permission or non-authority actors return `403 FORBIDDEN`.

Approved `invoke_sh4`, `invoke_cdsl`, and `present_blank_dated_cheque` decisions expose exactly one
future `execute_recovery` action requiring `recovery.action.initiate`. `continue_follow_up`,
`no_action`, and any other specifically configured retained decision expose no executable action;
011F owns actual execution and any further configured action mapping.

## Communication exception queue (009H9B)

`GET /api/v1/communication-exceptions/`

`GET /api/v1/communication-exceptions/{communication_exception_id}/`

`POST /api/v1/communication-exceptions/{communication_exception_id}/resolve/`

These protected operator routes expose only exceptions assigned to the current user. The actor must
retain the source send authority for the exhausted job type:
`communications.communication.send` for generic communications or
`finance.disbursement.send_advice` for advice. The dispatcher applies the assigned-owner filter in
addition to that permission, so another operator's exception is never projected.

The collection/detail item is deliberately redacted:

```json
{
  "communication_exception_id": "uuid",
  "provider_code": "email",
  "job_type": "generic",
  "related_entity_type": "loan_application",
  "related_entity_id": "uuid",
  "last_error_code": "worker_crash",
  "retry_count": 3,
  "assigned_owner": "current_user",
  "resolution_action": null,
  "resolved_by": null,
  "resolved_at": null,
  "resolution_version": 1
}
```

`provider_code` is the source delivery channel vocabulary (`email` or `sms`), independently of the
configured adapter implementation. The collection accepts only `page` and `page_size`, defaults to
page 1 with 20 rows, caps `page_size` at 100, orders by newest creation then descending exception
UUID, and returns the standard truthful top-level pagination object. Duplicate, unknown,
non-integer, non-positive, over-cap, or out-of-range pagination input returns
`400 VALIDATION_ERROR`. Every page is filtered independently by assigned owner and the exact
current permission selected by `job_type`; a generic-only operator never sees advice rows and an
advice-only operator never sees generic rows.

Recipient/address, subject/body/content, provider external id/error/secret, bank/UTR, idempotency
key, payload/digest, request id, actor identity/role/team, IP address, and user agent are absent. One
urgent assigned notification links to the protected detail route.

Resolution accepts exactly:

```json
{
  "resolution_action": "manual_closed",
  "resolution_version": 1
}
```

The version is a positive stale-write token. Unknown/malformed fields return
`400 VALIDATION_ERROR`; missing authority returns `403 FORBIDDEN`; an unsupported `retry`, stale
version, already-resolved row, or changed/missing exhausted-job evidence returns `409 CONFLICT`;
wrong-owner and wrong-job-kind authority remain nondisclosing. Since the job has reached its
retained `max_attempts`, this contract does not grant
another attempt. Manual closure leaves the job `failed`, preserves its attempts and provider
evidence, does not mutate the Communication to sent, and appends one audit/workflow resolution
chain. The opening terminalisation likewise appends one singular exception/audit/workflow chain.

## Payment initiation (009E/009E2/009E3)

`POST /api/v1/loan-accounts/{loan_account_id}/disbursements/initiate/` implements source §31.2.
It requires an `Idempotency-Key` header and a JSON object containing exactly:

```json
{
  "disbursement_amount": "400000.00",
  "borrower_bank_account_id": "uuid",
  "source_bank_account_id": "uuid",
  "final_verification_comments": "All current facts verified."
}
```

Only an active persisted `senior_manager_finance` actor with the Critical
`finance.disbursement.initiate` grant and newest-SAP-assignee loan scope may act. The owner calls
only `DisbursementReadinessModule.evaluate_for_initiation(actor, loan_account_id)` for one typed
composite payment-gate decision; the ordinary GET projection never exposes its evidence identities.
The decision freezes the exact canonical 23-check digest plus SAP, borrower-bank, governed
source-bank account/governance/version/audit identities, and the loan owner's exact creation status-
history/audit/workflow identities. A mutable row merely labelled SFPCL/RBL/
verified/active never passes. Source-bank activation requires the unseeded Critical
`config.source_bank_account.activate` grant, a reason and request id, and creates one singular
versioned/audited current decision. Replacement appends an exact predecessor link, deactivation
version/audit, and closed effective range while retaining the original activation proof; malformed,
duplicate, cross-linked, or incomplete history fails closed. The mandatory audit action is
`config.changed` and no production role receives the activation grant by default.

Success returns only:

```json
{
  "disbursement_id": "uuid",
  "initiation_status": "initiated",
  "authorisation_status": "pending",
  "bank_transfer_status": "pending"
}
```

The amount must be positive, fit numeric 18,2, and be no greater than both immutable loan terms and
sanction; source-defined positive lesser amounts are valid and the exact accepted amount is frozen
for CFC review. Creation atomically retains the manual-payment row, safe initiation audit/workflow, and one urgent
role-scoped CFC task. It does not authorise or execute the transfer, create a UTR/advice, fund or
activate the account, update a register, or communicate with the borrower. Exact key/payload/current
request replay returns `{ "idempotency_replayed": true, "original_response": <four-field success> }`
without writes. The supplied `X-Request-ID`, or a generated non-empty id when absent, and the SHA-256
digest of trimmed final-verification comments reconcile across the audit, workflow, and CFC task.
Changed key facts or a second active initiation return `409 CONFLICT`; readiness blockers use stable
`APPROVAL_PENDING`, `DOCUMENTATION_INCOMPLETE`, `SECURITY_PACKAGE_INCOMPLETE`,
`SAP_CUSTOMER_CODE_REQUIRED`, `BANK_ACCOUNT_NOT_VERIFIED`,
`DISBURSEMENT_EXCEEDS_SANCTION`, or `INVALID_STATE_TRANSITION`. Unknown/malformed fields return
`400 VALIDATION_ERROR`; inaccessible ids return nondisclosing `403 OBJECT_ACCESS_DENIED`.

## CFC disbursement authorisation (009F)

`POST /api/v1/disbursements/{disbursement_id}/authorise/` implements source §31.3 without an
`Idempotency-Key`. The JSON object contains exactly required `decision` (`approved` or `rejected`)
and required trimmed `comments` of at most 2,000 characters. Unknown fields/query parameters and
malformed values return `400 VALIDATION_ERROR`.

Only an active persisted actor with an active governed `chief_financial_controller` authority, the
Critical `finance.disbursement.authorise` grant, and the exact pending CFC-task/disbursement relation
may act. Primary role, permission, intake assignment, or an unknown/inactive authority alone grants
nothing; missing and inaccessible ids return nondisclosing `403 OBJECT_ACCESS_DENIED`. The checker
must differ from the retained Senior Manager Finance maker.

Success returns only the disbursement id, terminal authorisation status, still-pending bank-transfer
status, UTC `authorised_at`, and server-owned `next_action` (`record_bank_transfer` after approval,
`none` after rejection). It atomically freezes the checker role/team, comments digest, request and
network context, exact initiation/readiness digest, action identity, audit, workflow transition, and
CFC-task completion. It creates no bank transfer, UTR, disbursed timestamp, advice, register update,
funded balance, account activation, schedule, repayment, checklist action, or borrower communication.

Authorisation locks and reconciles the exact 009E2 initiation/audit/workflow/task ledger, beneficiary
and source-account relations, unfunded sanctioned account, request/final-verification digests, and
current governed source-bank account/governance/version/audit identities. It does not re-run legal,
security, approval, SAP, checklist, or 23-check readiness owners. Changed/replaced/incoherent evidence
returns zero-write `409 CONFLICT`. Exact terminal decision/comments replay returns the retained
projection without writes only while the complete terminal ledger remains coherent; changed or
opposite replay returns `409 CONFLICT`.

## Bank transfer success and loan activation (009G)

`POST /api/v1/disbursements/{disbursement_id}/mark-transfer-successful/` implements source §31.4.
It requires `Idempotency-Key` and exactly `bank_reference_number`, timezone-aware `disbursed_at`, and
`bank_transfer_evidence_document_id`. The reference is NFKC-normalized, trimmed, whitespace-
collapsed, uppercase, nonempty, at most 120 characters, and globally unique; duplicates return
`409 DUPLICATE_BANK_REFERENCE`. Time cannot precede CFC authorisation or exceed A-127's five-minute
future tolerance. Evidence must be a checksum-current immutable `restricted`/`finance` upload
scoped to the exact `loan_application` or `loan_account`.

Only an active persisted exact CFC checker or exact Senior Manager Finance initiating maker may act,
and only with the Critical `finance.disbursement.mark_success` grant. Role, permission, intake
assignment, another CFC/Senior Finance user, or an inaccessible id is insufficient; missing and
out-of-scope ids use nondisclosing `403 OBJECT_ACCESS_DENIED`.

The workflow consumes the locked 009F2 typed approved decision and reconciles its terminal
authorisation tuple, frozen initiation/readiness/bank/loan-creation evidence, exact unfunded
sanctioned account/terms, and current evidence checksum. Pending/rejected, stale, partially funded,
active, over-sanction, changed-owner, bad-time, cross-object, or already-transferred facts fail
without success artifacts. Success returns only `disbursement_id`, `bank_transfer_status:
successful`, `loan_account_status: active`, and the stable protected pending
`disbursement_advice_communication_id`. The final field is an advice/outbox identity, not a sent or
provider-accepted claim.

Atomically it creates one unique manual transfer/evidence, funds disbursed/principal/total with the
exact amount, keeps interest/charges zero, sets tenure start, activates the account, links one
sanctioned-to-active history, creates one exact Loan Register update, and creates one pending advice
intent. The register and intent each bind the transfer/account/application/member/amount, reference
digest, file/checksum, transfer action/evidence digest, audit, and workflow identities. Only this
singular coherent register evidence permits `loan_register_updated_flag: true`. Safe audit/workflow
evidence keeps only masked/reference digest, evidence id/checksum, owner/action ids, amount/status,
actor role/team, and request/network context.

Exact normalized key/payload/actor retry returns API §45.2's
`{idempotency_replayed: true, original_response: <retained first response>}` with no write.
Changed key/payload, changed retained success ledger, duplicate UTR, or a concurrent loser returns a
stable conflict. Missing, duplicate, cross-linked, or changed register/advice-intent evidence also
fails closed. The action sends no advice, signs no checklist, and creates no repayment, schedule,
interest, or borrower-visible truth; 009H2 owns delivery of the stable pending identity.

## Disbursement advice (009H-009H5)

`POST /api/v1/disbursements/{disbursement_id}/send-advice/` implements source §31.5 with exactly
`channel` and `recipient_email`; query parameters and unknown fields are rejected. MVP accepts only
normalized `email`, and the address must equal the exact member's current canonical email. Caller
text, recipient identity, template, transfer facts, and delivery outcome are never accepted from
the request.

Only an active persisted Senior Manager Finance user who is both the exact initiating maker and the
current exact SAP assignee, or an active Credit Manager in the canonical active-loan/application
scope, may act with the High `finance.disbursement.send_advice` grant. CFC-only authority is denied.
An effective multi-role user acts only through a source-authorised role. Missing or out-of-scope ids
use nondisclosing `403 OBJECT_ACCESS_DENIED`; role, permission, raw ids, borrower contact, or intake
scope alone are insufficient.

The workflow locks and reconciles the complete current 009G transfer/audit/workflow/history,
unique transfer, active exactly funded account, member/application/account relation, and canonical
contact. It requires exactly one approved effective borrower email template whose declared and
used variables are exactly borrower name, application reference, account number, sanctioned and
disbursed amounts, date, and masked bank reference. Missing, ambiguous, stale, unfunded, or
malformed evidence returns zero-write `409 CONFLICT`.

Both `POST /api/v1/communications/send/` and
`POST /api/v1/disbursements/{disbursement_id}/send-advice/` require a trimmed nonblank
`Idempotency-Key` of at most 255 characters. The communications owner binds the key to the exact
communication/advice, frozen payload, and current actor. Exact replay returns retained current
truth; missing, changed, cross-actor, or cross-object reuse returns zero-write validation/conflict.

The advice request consumes the exact pending advice UUID created by transfer success, freezes the current
actor/role/team/request/network and rendered-template identity, and creates or reconciles one durable
communications-owned job without invoking a provider. Its initial response contains only
`disbursement_id`, `communication_job_id`, `delivery_status: queued`, and UTC `queued_at`. Exact
actor/channel/recipient replay returns the same job; changed replay conflicts. Queuing alone does not
create a Communication, mark advice sent, or make advice borrower-visible.

The pinned Celery application explicitly registers the generic/advice execution task and periodic
due/recovery task. Broker, result backend, adapter, beat interval, claim lease, and batch limit are
environment-driven; tests use in-memory transports. A new job publishes one named signature only
from a robust transaction commit callback: rollback publishes nothing, and broker publication
failure leaves the committed queued row reachable by the periodic scan.

The asynchronous worker re-authorises the frozen actor against current disbursement truth and uses
the same canonical dispatcher contract for generic and advice jobs. Manual/no-provider mode never
returns acceptance; only the test Fake or a configured external adapter may produce `sent`. Job lifecycle is
`queued` → `running` → `retrying`/`sent` or terminal `failed`; provider timeouts, rejection, malformed
results, and crashes retain only a bounded safe failure code and exponential backoff for at most three
attempts. Exhaustion creates an operator task but no fabricated sent advice. Provider identity remains
stable across fresh worker instances and a transaction rollback after acceptance. Running claims
carry a fenced UUID and expiry. Stale recovery increments a separate recovery count without resetting
attempts; an expired worker cannot mutate its replacement. H6 legacy-partial advice is never selected
or mutated and is projected only as operator-blocked. Worker/operator results expose job/status/
attempt/schedule/lease/recovery/safe-failure facts, never recipient/body/provider/financial/token/
actor/request/payload facts.

After acceptance, the workflow atomically marks that intent `sent`, retains one protected `sent`
communication snapshot/link, and records one `disbursement.advice_sent` audit and
`DisbursementAdviceSent` workflow event. The protected communication is the only retained row
containing the full recipient address. General audit evidence stores only a masked address and
SHA-256 digest plus protected owner/communication, template/provider, sender role/team,
request/network, and upstream evidence identities.

After worker acceptance, exact replay includes `communication_job_id` with the terminal
`disbursement_id`, `disbursement_advice_communication_id`, `delivery_status: sent`, and UTC `sent_at`
projection without writes only while the current canonical email, approved/effective template
identity/version/variables, freshly rendered subject/body, provider id/status/time, sender role/team,
transfer/register/intent, audit, action, workflow, outbox, and job facts remain exact. Any drift
returns zero-write `409 CONFLICT`; historical delivery is never returned as current. The action never
changes money, transfer/CFC state, loan status/terms, Loan Register, checklist, repayment, schedule,
or interest truth. MP14 must treat advice as issued only from this terminal accepted/finalized chain.

## Tri-party agreement verification (008G/008G2)

`POST /api/v1/loan-documents/{loan_document_id}/verify/` implements source §26.6 only for a
`tri_party_agreement` retained by the current renderer contract. The request contains exactly:

```json
{
  "verification_status": "verified",
  "remarks": "Borrower and nominee execution verified."
}
```

Both fields are required; `verification_status` has only the success value `verified`, while
`remarks` is a nullable, trimmed string of at most 4,000 characters. The action requires
`documents.loan_document.verify`, active Company Secretary authority, and a sanction-approved
Stage-4 parent. Permission and role are checked before payload and object lookup. A Compliance
preparer, read-only actor, permission-only actor, wrong-stage parent, or unrelated scope receives
403; an otherwise authorised absent or wrong-type id receives the established nondisclosing 404.
Legacy/mismatched renderer provenance returns zero-write `409 CONFLICT`.

Verification consumes only the approval owner's canonical frozen subsidiary-route fact. The fact
must be complete and unanimously true; false is not applicable, while missing, malformed, or
conflicting truth remains a zero-write conflict. It also consumes exactly one borrower and one
selected-nominee row from the legal owner's exact-document signature selector. Both must retain the
canonical captured party id/name, `signed` state, signed time, non-null Compliance capture maker,
and no mismatch/resolution; the Company Secretary checker must differ from each capture maker.
Cross-document, wrong-party, duplicate, pending, mismatch, resolved, or legacy null-maker rows do
not satisfy execution.

Success returns the standard §6.3 action response. Exact replay returns the same retained workflow
identity; a changed remark returns a new verified-to-verified action identity:

```json
{
  "entity_type": "loan_document",
  "entity_id": "uuid",
  "previous_status": "pending",
  "new_status": "verified",
  "workflow_event_id": "uuid",
  "available_actions": []
}
```

An exact replay is zero-write. A changed retained remark is a new attributable checker correction
with complete old/new audit, version, and workflow evidence. Verification freezes each consumed
borrower/nominee signature id, party id/type, canonical name, current capture maker, and signing
time. Ordinary capture cannot mutate a consumed signature while the agreement remains verified.
Loan-document list and legal checklist
reads project the current verification status/verifier/time/remarks, but the action does not change
execution, generation, stamp/notary, file/download, checklist completion/verifier/remarks/signature,
package, security, repayment, or disbursement-readiness truth. A missing, inapplicable, or differently
linked tri-party checklist projection rolls the document mutation and all success ledgers back.

Pending stamp/notary preparation and signature capture now transfer maker identity on every
material change; replay does not. A later editor therefore cannot verify/resolve their own facts by
switching roles. New positive/adverse stamp/notary outcomes and mismatch resolutions are also
database-constrained to non-null, distinct maker/checker ids. Pre-008G2 null-maker rows are marked as
legacy during migration, remain readable/replayable history, and cannot be changed or supply new
downstream truth. Unresolved mismatch overwrite returns HTTP 400 with
`SIGNATURE_MISMATCH_UNRESOLVED`, not generic conflict.

## Post-sanction documentation checklist (008C/008C2)

`GET /api/v1/loan-applications/{loan_application_id}/document-checklist/` returns the persisted
source §27.1 legal checklist once the application is sanction-approved. Before sanction, the same
route retains the 005D application-intake checklist response under A-104 so the existing completeness
workbench remains compatible. The existing `/document-checklist/refresh/` POST remains a read-derived
005D compatibility endpoint only; 008C adds no public legal refresh, completion, or approval action.

The legal GET requires `documents.checklist.read` plus source-authorised application scope. Compliance
Team and Company Secretary can read sanction-approved documentation applications; Credit Manager uses
canonical application scope; a sanction approver can read only an attributable approval cycle; an
auditor requires the retained audit-read scope grant. Permission-only or unrelated actors receive
`403 OBJECT_ACCESS_DENIED`; missing global permission receives `403 FORBIDDEN`. Reads never write.
That authority decision now runs before checklist existence, item counts, metadata, or serialization.
Only a Compliance Team actor holding the legal read permission receives `404 NOT_FOUND` for an
unknown application; other legal-read roles remain nondisclosing. A-104's pre-sanction compatibility
continues through the application-owned read boundary.

Success uses the standard envelope and this metadata-only data shape:

```json
{
  "document_checklist_id": "uuid",
  "loan_application_id": "uuid",
  "checklist_status": "in_progress",
  "items": [
    {
      "checklist_item_id": "uuid",
      "item_code": "term_sheet",
      "item_label": "Term Sheet",
      "required_flag": true,
      "applicable_flag": true,
      "completion_status": "pending",
      "applicability_source": "source_always_required",
      "applicability_blocker": null,
      "loan_document_id": "uuid-or-null"
    }
  ],
  "signature_status": {
    "company_secretary": "pending",
    "credit_manager": "pending",
    "sanction_committee": "pending",
    "senior_manager_finance": "not_applicable_until_disbursement"
  }
}
```

Items are ordered as witness PAN/Aadhaar, cancelled cheque, blank-dated cheque, PoA, conditional
tri-party, conditional SH-4, conditional CDSL pledge, Term Sheet, Loan Agreement, conditional Bank
Verification Letter, and final checklist. Applicable requirements start `pending`; inapplicable
conditionals start `not_applicable`. Missing/conflicting source facts carry explicit blockers and are
never guessed. A retained 008B generated-document id may be linked through legal metadata only and
never changes completion, execution, verification, stamp, notary, signature, or approval state.
Current renderer-provenance linkage writes `document_checklist.linkage_changed`, not
`document_checklist.applicability_changed`; legacy-unverified output remains unlinked.

The public sanction-approval route atomically creates one checklist and one row per item through a
top-level process coordinator. A terminal approval attempted through the lower-level domain interface
without that coordinator raises `409 SANCTION_COMPLETION_REQUIRED` and writes nothing. Exact replay/unchanged internal
refresh writes nothing. Real creation writes attributable `document_checklist.created` audit plus
`documentation_checklist` workflow evidence; a real applicability change retains old/new item facts
and its source reason. Request id, IP address, user agent, actor role, and actor team are retained in
checklist audit evidence. Refresh preserves completion/verifier/time/remarks, checklist status, and
signature facts. An applicability reversal that contradicts completed evidence returns an internal
atomic conflict until the owning correction workflow resolves it. PostgreSQL application locking and
database uniqueness preserve one sanction decision/checklist/item ledger under five final-sanction
attempts.

## Credit Sanction Register legacy-null frontend contract (007T)

The retained `GET /api/v1/credit-sanction-register/` backend contract is now represented exactly by
the frontend DTO and S23 detail. Historical rows created without frozen source/terminal JSON return
top-level `purpose: null` and `risk: null`, nullable `folio_number`/`loan_type`, empty approver arrays,
and nullable rejection/condition/communication facts. The frontend renders those values as
unavailable without reconstructing them from current member, application, appraisal, user, or
communication state. Modern non-null row fields, actor/object scope, strict standard pagination,
and the read-only register interface are unchanged.

## Shared authenticated permission denial (002J2)

Authenticated users who lack a required global permission receive HTTP `403` with error code
`FORBIDDEN`, matching `docs/source/api-contracts.md` §7.1. The shared envelope boundary also
normalizes the retired `PERMISSION_DENIED` code for compatibility, while production callers and the
typed object-access seam emit `FORBIDDEN` directly. Authentication/token errors and the specialized
`OBJECT_ACCESS_DENIED`, `SENSITIVE_FIELD_ACCESS_DENIED`, and `APPROVAL_AUTHORITY_REQUIRED` codes are
unchanged. This is a response-contract alignment only: permission grants, role assignments, object
scope, status codes, messages, successful payloads, audit behavior, and workflow behavior did not
change.

Source contract baseline: `docs/source/api-contracts.md`.

This working file tracks implementation status and slice-level decisions. It must be updated whenever a slice changes frontend/backend assumptions.

## Dev Setup

Backend development uses environment-driven Django settings and a persistent local SQLite database at
`sfpcl_credit/db.sqlite3`. After dependencies are installed from `sfpcl_credit/requirements-dev.txt`,
run:

```bash
/Users/amitkallapa/Loan\ Management\ System\ Development/.ralph/venv/bin/python sfpcl_credit/manage.py migrate
/Users/amitkallapa/Loan\ Management\ System\ Development/.ralph/venv/bin/python sfpcl_credit/manage.py runserver 127.0.0.1:8000
cd sfpcl-lms && npm run dev
```

The React dev server origin `http://localhost:5173` is allowed by default for local CORS. Override
with `SFPCL_CORS_ORIGINS` as a comma-separated list when needed.

For local demonstrations, deterministic staff demo users are available only after the
guarded seed command is run with both local flags enabled:

```bash
SFPCL_DEBUG=true SFPCL_ALLOW_DEMO_SEED=true \
/Users/amitkallapa/Loan\ Management\ System\ Development/.ralph/venv/bin/python sfpcl_credit/manage.py seed_demo_users
```

The command calls the canonical role/team/permission catalogue seed first, updates only
`demo.*@sfpcl.example` users, and keeps E2E-only users separate. Predictable credentials
are local/dev only; do not use or promote them as production credentials. Demo login and
`/auth/me` examples are saved in `.ralph/runs/2026-07-04_184602_normal_run/api-response-examples.md`.

| Contract Area | Status | Related Screens | Source Contract | Notes |
|---|---|---|---|---|
| Backend health endpoints | Implemented in slice 002A; envelope unified in 002C2 | None | `technical-architecture.md` R1 health checks; standard response envelope from `api-contracts.md` §6.1 | `GET /api/v1/health/live/`, `/ready/`, and `/deep/` return `{ success, data, meta }` via the shared envelope helper; `meta` now includes `request_id`, `timestamp`, and `api_version: "v1"`. Ready/deep include database connectivity status. |
| Authentication and current user | Current-user implemented through slice 002D; frontend shell wired in 002E; member portal auth implemented in 005FA | Login, dashboards, MP00, MP01, MP02, MP25 | `docs/source/api-contracts.md`, `auth-permissions.md`, `screen-spec-member-portal.md` | Implemented `POST /api/v1/auth/login/`, `/refresh/`, `/logout/`, and `GET /api/v1/auth/me/` with standard envelopes, active-user-only access, refresh rotation, session revocation, role/team token claims, effective role permissions, current action availability, and auth audit logs for login/refresh/logout. 005FA adds portal activation/login/password-reset/password-change endpoints under `/api/v1/portal/auth/`; borrower access tokens and `/auth/me` include `member_id`, `portal_account_id`, and `portal_role = borrower_member` while exposing only portal own-data permissions, not staff completeness/deficiency permissions. The React shell now logs in staff through `/auth/login/`, member portal users through `/portal/auth/login/`, stores bearer/refresh tokens in local browser storage, loads `/auth/me/` before rendering protected navigation, clears local state on `TOKEN_EXPIRED`/`INVALID_TOKEN`, and posts the refresh token to `/auth/logout/`. Admin session controls remain future slices. |
| Admin user management | Implemented in slice 002G; action-specific permission gating added in 002G2 | Admin User Management | `api-contracts.md` §6-7, §11.4, §12; `auth-permissions.md` §12.1, §15.12, §19 | `GET /api/v1/admin/users/`, `GET /api/v1/admin/users/{user_id}/`, and assignment action endpoints bind existing `Role`/`Team` catalogue rows only. All routes require session-bound bearer auth. Since 002G2 each action requires the specific canonical user-admin permission (`auth-permissions.md` §12.1), not just any user-admin grant: list/detail read requires `users.user.read` OR any write user-admin permission (read fallback per A-015 because seeded `system_admin` lacks `users.user.read`); role assignment and team add/remove require `users.user.update`; suspending a user requires `users.user.disable`; restoring a user to active requires `users.user.update`. A partial-permission actor receives `403 FORBIDDEN` with no `AuditLog` write and no session revocation. Order of checks: `401` (auth) → `403` (permission) → `400`/`404`. Successful role/team/status changes write `AuditLog`; suspending a user revokes active sessions; changing/suspending the last active `system_admin` is blocked per A-014. The frontend continues to map the write user-admin permissions to prototype `manage_users` for nav/route visibility. |
| Early end-to-end tracer | Implemented in slice 002EX | Staff Tracer screen | `docs/source/api-contracts.md` §3-6; `docs/source/data-model.md` §26.1-26.2 | Thin dev proof only. Protected by session-bound bearer auth and explicit `tracer.lifecycle.run` permission. Endpoints: `POST /api/v1/tracer/members/`, `POST /api/v1/tracer/members/{member_id}/loan-applications/`, `POST /api/v1/tracer/loan-applications/{loan_application_id}/sanction/`, `POST /api/v1/tracer/loan-applications/{loan_application_id}/loan-account/`, `POST /api/v1/tracer/loan-accounts/{loan_account_id}/disburse/`, `POST /api/v1/tracer/loan-accounts/{loan_account_id}/repayments/`, `POST /api/v1/tracer/loan-accounts/{loan_account_id}/close/`. Minimal models only; every transition writes `audit_logs` and `workflow_events`; invalid state transitions return `409 INVALID_STATE_TRANSITION`; missing/revoked auth returns the standard `401` envelope before domain writes. |
| API contract test harness | Implemented in slice 002J | None | `api-contracts.md` §6.1-6.4, §7.1-7.3, §44 | Test-only assertions live in `sfpcl_credit/tests/api_contracts.py`. Future endpoint slices should use them to prove standard success envelopes, error envelopes, top-level list pagination, and target §44 `available_actions` item shapes without importing test utilities from production code. The harness regression tests cover `/auth/me/`, admin users pagination, `401 AUTH_REQUIRED`, revoked-session `401 INVALID_TOKEN`, `403 FORBIDDEN`, partial-admin write denial, and tracer `409 INVALID_STATE_TRANSITION`. A-016 records that current `/auth/me/` still returns flat permission-code strings for `available_actions`; the object shape is asserted against an internal sample for future detail endpoints. |
| Local demo staff seed | Implemented in slice 002K; corrected in 002K2 | Login, dashboard smoke, admin/tracer permission smoke | `implementation-roadmap.md` §10, §20-22; `technical-architecture.md` §8-12, §17-18; `auth-permissions.md`; `api-contracts.md` §11-12, §43-44 | `python manage.py seed_demo_users` is a guarded local/dev seed path. It refuses unless `SFPCL_DEBUG=true` and `SFPCL_ALLOW_DEMO_SEED=true`, calls `seed_catalogue()`, creates or updates deterministic `demo.*@sfpcl.example` staff users with active primary roles and memberships, and does not alter `e2e.*` users. Demo users authenticate through the real `/auth/login/` and `/auth/me/` endpoints; there is no demo auth bypass. The zero-permission user returns `permissions: []` and `available_actions: []`; the tracer-only user uses the guarded local/dev-only `local_demo_tracer_user` role and returns only `tracer.lifecycle.run`; the shared source-catalogue `sales_team_user` role remains permission-neutral until source documents define grants; system admin preserves canonical action-specific user-admin permissions without broad `manage_users` aliases. |
| Role/permission/team catalogue | Seeded in slice 002C; exposed for current user in 002D | None directly | `auth-permissions.md` §12-15, §38 | Canonical `Permission`, `Role`, `Team`, `RolePermission` catalogue seeded idempotently via `python manage.py seed_role_catalogue` (`sfpcl_credit/identity/catalogue.py`). `/api/v1/auth/me/` exposes the authenticated user's effective permission codes from this data. |
| Members and KYC | Member directory list implemented in 004A; masked member profile detail implemented in 004B; nominee list/create implemented in 004D; shareholding list/create implemented in 004F; land/crop list/create implemented in 004G; KYC profile/document upload/verify implemented in 004H; member bank-account/cancelled-cheque metadata implemented in 004J; Borrower 360 Epic 004 UI wiring implemented in 004K with corrective DTO hardening queued in 004K2 | Member Directory, Member Profile, borrower profile, application intake | `api-contracts.md` §13.1/§13.3/§13.5/§14.1-§14.3/§15.1-§15.2/§17.1-§18.4; `data-model.md` §10.1-§10.4/§11.1/§11.7-§12.4; `auth-permissions.md` §12.2-§12.3/endpoint map | `GET /api/v1/members/` is API-backed with standard list pagination, `members.member.read`, masked mobile numbers, no PAN/Aadhaar fields, and strict §13.1 query validation. `GET /api/v1/members/{member_id}/` returns masked PAN/Aadhaar objects, address, profile shell fields, share/active-member shell fields, and object-shaped `available_actions[]`. `GET/POST /api/v1/members/{member_id}/nominees/`, `/shareholdings/`, `/land-holdings/`, `/crop-plans/`, `/bank-accounts/`, and `/cancelled-cheques/` are API-backed with their documented validations and metadata-only create audits. `GET/POST/PATCH /api/v1/kyc-profiles/`, KYC document upload, and KYC document verify are implemented for member parties only with KYC permissions. Sensitive bank-account reveal, re-KYC task management, share certificate/demat, bank verification letters, disbursement bank gates, and loan-application/loan-account/repayment/risk/audit Borrower 360 data remain future scope. |
| Loan applications | Draft create/read/update implemented in 005A; submit in 005B; reference generation/register persistence in 005C; object access hardened in 005C2; application document/checklist metadata implemented in 005D; completeness workbench/pass implemented in 005E; deficiency return/list/resolve implemented in 005F; rejection-note create/send shell implemented in 005H; staff list/register UI wiring reads implemented in 005I; staff detail rejection-note summary hardening implemented in 005I2; eligibility assessment through default/document/terms/purpose/nominee checks implemented in 006A-006B; loan-limit calculation and snapshots implemented in 006C-006D; cultivated-acreage source hardening implemented in 006C2 | Applications, completeness, rejection note shell, Loan Request Register, eligibility assessment, loan-limit assessment | `api-contracts.md` §8, §19.1-§23; `screen-spec.md` S13/S15; `data-model.md` §13.1, application-document/deficiency/rejection-note/register tables, and §14.1-§14.2; `auth-permissions.md` §12.4, §19.2, §34.3, §37.3 | Existing loan-application, register, document, checklist, completeness, deficiency, rejection-note, and eligibility endpoints retain their documented contracts. `POST /api/v1/loan-applications/{id}/loan-limit-assessment/calculate/` requires a stored normally eligible assessment, same-member verified source facts, an application-linked verified crop plan, agreement among applicable cultivated-acreage evidence, an active Board-referenced policy version, `credit.loan_limit.calculate`, and existing application object access; it atomically snapshots the lower of shareholding/land limits with audit and workflow evidence. Staff detail reads include nullable `rejection_note` summary metadata when a staff rejection note exists; `application_status` remains backend-owned and unchanged by the summary. Staff list reads support standard `search`, `application_status`/`status`, `current_stage`, `member_id`, `ordering`, `page`, and `page_size` with `page_size` capped at 100. Register reads support `search`, `register_status`/`status`, `current_stage`, `member_type`, `ordering`, `page`, and `page_size`. Appraisal, sanction, document generation, real communication delivery, and disbursement remain future slices. |
| Appraisal and loan limit | Eligibility/loan limit implemented through 006D2C; appraisal preparation, frozen provenance, Credit Manager review/return/rejection, immutable review history, and legacy remediation implemented through 006E4 | Appraisal workbench | `functional-spec.md` §9.8/M04; `api-contracts.md` §22-§24 | Appraisals freeze canonical redacted eligibility and loan-limit projections, block unproven legacy provenance until explicit scoped revalidation, enforce both `credit.appraisal.review` and active `credit_manager` role authority, retain every review reason in appraisal-owned append-only history, and create the existing rejection-note draft for terminal rejection. Legacy draft and review-pending rows can pin current projections without inheriting review authority; a legacy reviewed row reopens to draft and requires maker resubmission plus fresh Credit Manager review. Rejected/submitted terminal rows remain quarantined for governed repair. |
| Sanction and approvals | Approval workflow, workbench, registers, settings, frozen legacy history, strict pagination, and action-order closure implemented through 007T | Sanction workbench, registers, approval settings | `auth-permissions.md`, `api-contracts.md` §25/§44, `screen-spec.md` S21-S25 | Approval matrix is high-control; case reads/actions use frozen actor-scoped projections. Historical S23 `purpose`/`risk` are top-level nullable, and S21 queue/detail/action/decision refreshes share newest-request authority. |
| Documentation and securities | Document-file upload foundation implemented in 003C; secure download descriptor implemented in 003D; broader loan document workflows remain draft | Documentation hub | SOP PDFs, `api-contracts.md` §26; `data-model.md` §16.1 | `POST /api/v1/document-files/` stores file bytes outside the database through the local adapter and stores metadata in `document_files`. `GET /api/v1/document-files/{document_id}/download/` returns a permissioned, time-limited local download descriptor and writes document-access audit. Checklist, template, signature, stamp, notarisation, and loan-document flows remain future slices. |
| Versioned configuration | Loan-policy shell implemented in 003E; calculations and broader config types remain draft | Settings/config shell | `api-contracts.md` §41.1, §42.3; `data-model.md` §25.1, §26.3; `functional-spec.md` M01-FR-001/M01-FR-002/M01-FR-015 | `loan_policy_configs` and `version_histories` are persisted. `GET/POST/PATCH/activate` loan-policy APIs and filtered version-history reads are protected, audited where mutating, and versioned on activation. M01-FR-003 through M01-FR-014 calculations/rules are explicitly deferred; only neutral source model fields are stored. |
| Communication templates and communication history | Canonical dispatcher, generic/advice jobs, and recoverable Celery runtime implemented through 009H8 | None directly | `api-contracts.md` §39.1-§39.3; `integrations.md` §§7.3/10/21/22/29/33.3; `data-model.md` §24.1-§24.2 | `content_templates`, `communications`, protected advice outboxes/provider attempts, and fenced communication jobs are persisted. Generic `POST /api/v1/communications/send/` and disbursement advice share the dispatcher-owned approved/effective template, exact merge/render, Communication, safe-audit, configured-adapter, on-commit enqueue, bounded retry, stale recovery, and operator-safe evidence policy. HTTP queueing remains provider-free; the registered worker alone may produce configured-provider acceptance. |
| SAP and disbursement | SAP request/delivery/completion/reuse implemented through 009B3B; loan-account/readiness, payment initiation, CFC decision, transfer success, advice delivery, and borrower MP14 projection implemented through 009I | Disbursement, CFC, and MP14 | `api-contracts.md` §§29-31; `integrations.md` §§8-10/19/21 | SAP is manual/adapter-first for MVP and owned by the public `sap_workflow` module; disbursement owner decisions feed a masked own-member portal projection, and finalized communications owns the one-use advice artifact boundary. Staff finance/CFC frontend wiring remains 009K. |
| Loan account, repayment, interest | Draft from source | Loan account, repayments, interest | `data-model.md`, `api-contracts.md` | Financial calculations are high risk. |
| Default, recovery, closure | Draft from source | Default, closure | `functional-spec.md`, `api-contracts.md` | Recovery approvals require audit evidence. |
| Compliance, registers, reports | Draft from source | Compliance, registers, reports | `api-contracts.md`, `auth-permissions.md` | Export masking must be tested. |

## Contract Rules
- Do not implement API-consuming frontend code without a matching contract entry.
- Do not treat mock data shape as the final backend shape without checking `docs/source/api-contracts.md` and `docs/source/data-model.md`.
- Mark uncertain contracts as Draft and record assumptions in `ASSUMPTIONS.md`.

## Implemented Auth Subset

Implemented endpoints:

| Endpoint | Request | Success Data | Key Rules |
|---|---|---|---|
| `POST /api/v1/auth/login/` | `email`, `password` | bearer `access_token`, `refresh_token`, `expires_in`, user profile with role/team codes | Only `active` users receive tokens; invalid credentials and non-active users receive `401 INVALID_CREDENTIALS`; successful and failed attempts are audited. |
| `POST /api/v1/auth/refresh/` | `refresh_token` | rotated bearer token payload | Refresh tokens are matched against `user_sessions.refresh_token_hash`; successful refresh rotates the token; replayed, revoked, expired, malformed, or status-invalid tokens return `401`. |
| `POST /api/v1/auth/logout/` | `refresh_token` | `{ "logged_out": true }` | Logout revokes the matching session with reason `logout`; the same refresh token cannot be used again; logout is audited. |
| `GET /api/v1/auth/me/` | `Authorization: Bearer <access_token>` | user identity (`user_id`, `full_name`, `email`, `mobile_number`, `status`), `roles`, `teams`, compatibility `role_codes`/`team_codes`, `permissions`, `available_actions` | Access token must be signed, unexpired, type `access`, and bound to an active `user_sessions` row for an active user. Missing token returns `401 AUTH_REQUIRED`; expired access tokens return `401 TOKEN_EXPIRED`; refresh/wrong-type, malformed, revoked-session, inactive-user, unknown-session tokens, or sessions linked to non-active portal accounts return `401 INVALID_TOKEN`. When a linked `PortalAccount` is suspended/inactive/deleted-member scoped, the active session is revoked with reason `portal_account_status_changed` before `/auth/me` returns. |

Member portal endpoints added in 005FA:

| Endpoint | Request | Success Data | Key Rules |
|---|---|---|---|
| `POST /api/v1/portal/auth/activation/start/` | `folio_or_member_id`, `contact`, optional `pan_last4`, optional `aadhaar_last4` | `challenge_id`, `masked_contact`, `expires_at` | Member/contact/last-four facts must match a non-deleted member; already-active accounts return `409 PORTAL_ACCOUNT_ACTIVE`; no full PAN/Aadhaar or OTP is returned. Creates an OTP challenge, a pending communication-shell row, and `portal.auth.activation.started` audit metadata. |
| `POST /api/v1/portal/auth/activation/complete/` | `challenge_id`, `otp`, `password`, `confirm_password` | `portal_account` with `portal_account_id`, `member_id`, `status`, masked contact facts | OTP must be pending and unexpired; password must match and be at least 10 characters. Creates/updates a `borrower_portal_user` user linked one-to-one to the member, activates the portal account, and writes `portal.account.activated`. |
| `POST /api/v1/portal/auth/login/` | `identifier`, `password` | bearer token payload plus user payload | Identifier may match portal user email, member email, or member mobile. Invalid/inactive/suspended cases return generic `401 INVALID_CREDENTIALS` and write `portal.login.failed`; successful login writes `portal.login.success`. Access tokens include `member_id`, `portal_account_id`, and `portal_role = borrower_member` only for active, non-deleted member portal accounts; `/auth/me` returns the active `borrower_portal_user` role, the same member scope, and only portal own-data permissions while the portal account remains active. |
| `POST /api/v1/portal/auth/password-reset/start/` | `identifier` | generic message plus challenge details when a valid account exists | Returns a generic response to avoid account enumeration; valid active portal accounts receive an OTP challenge and `portal.auth.password_reset.started` audit metadata. |
| `POST /api/v1/portal/auth/password-reset/complete/` | `challenge_id`, `otp`, `password`, `confirm_password` | `{ "reset": true }` | OTP is single-use and expiring; successful reset updates the password hash, revokes all active sessions with reason `portal_password_reset`, and writes `portal.auth.password_reset.completed`. Replay returns `400 OTP_INVALID`. |
| `POST /api/v1/portal/auth/password/change/` | bearer token plus `current_password`, `new_password`, `confirm_password` | `{ "password_changed": true }` | Requires a portal bearer session whose linked portal account is still active. Suspended/inactive portal accounts using old bearer tokens receive `401 INVALID_TOKEN` and the session is revoked with reason `portal_account_status_changed`. Current password must match. Successful change updates the password hash, revokes other active sessions with reason `portal_password_change`, keeps the current session active, and writes `portal.password.changed`. |

Full 002D3 current-user example responses are saved in `.ralph/runs/2026-07-03_214932_normal_run/api-response-examples.md`.

## Early tracer API (002EX)

The 002EX tracer is a deliberately thin integration proof, not the final member/application/finance contract. It follows the source API rules for versioning, envelopes, explicit action endpoints, backend-enforced transitions, and audit/workflow observability.

Rules:
- All endpoints require `Authorization: Bearer <access_token>`.
- The access token must validate through the session-bound auth path used by `/auth/me/`; logout/revocation returns `401 INVALID_TOKEN`.
- The authenticated user's effective permission list must include `tracer.lifecycle.run`; otherwise the API returns `403 FORBIDDEN`.
- Amounts must be positive decimal strings and are serialized as strings.
- Allowed status path: member `active`; application `draft -> sanctioned`; account `pending_disbursement -> active -> closed`; repayment `posted`.
- Every successful transition writes one `audit_logs` row whose action starts with `tracer.` and one `workflow_events` row.

Response examples for login, `/auth/me`, every tracer transition, and persistent SQLite counts are saved in `.ralph/runs/2026-07-03_234219_normal_run/api-response-samples.md`.

## Admin user management API (002G)

Implemented endpoints:

| Endpoint | Request | Success Data | Key Rules |
|---|---|---|---|
| `GET /api/v1/admin/users/?page=1&page_size=20` | `Authorization: Bearer <access_token>` | List envelope with `data[]` and top-level `pagination` | Requires session-bound active access token and canonical user-admin permission. Items use the `/auth/me/` role/team shape: `roles[{role_code, role_name}]`, `teams[{team_code, team_name}]`. |
| `GET /api/v1/admin/users/{user_id}/` | Bearer access token | One user item | Same permission and serialization shape as list. |
| `POST /api/v1/admin/users/{user_id}/roles/` | `{ "role_code": "accounts_head" }` | Updated user item | `role_code` must reference an existing active `Role`; this changes the user's required `primary_role`; writes `admin.user.role_assigned`. |
| `POST /api/v1/admin/users/{user_id}/teams/` | `{ "team_code": "credit_assessment" }` | Updated user item | `team_code` must reference an existing active `Team`; creates or reactivates a `UserTeamMembership`; writes `admin.user.team_added` when a membership changes. |
| `DELETE /api/v1/admin/users/{user_id}/teams/{team_code}/` | Bearer access token | Updated user item | Existing active membership is marked inactive; writes `admin.user.team_removed`. |
| `PATCH /api/v1/admin/users/{user_id}/status/` | `{ "status": "active" }` or `{ "status": "suspended" }` | Updated user item | Status is limited to `active`/`suspended`; setting `suspended` revokes active `UserSession` rows with reason `admin_status_suspended`; writes `admin.user.status_changed`. |

Rules:
- Missing bearer token returns `401 AUTH_REQUIRED`; malformed or revoked session-bound access tokens return the existing `401 INVALID_TOKEN`/`TOKEN_EXPIRED` envelope.
- Authenticated users without canonical user-admin permission return `403 FORBIDDEN`.
- Unknown role/team codes and unsupported statuses return `400 VALIDATION_ERROR` with `field_errors`.
- A-014 lock-out guard: any role or status change that would leave zero active users whose primary role is `system_admin` returns `400 VALIDATION_ERROR`.
- Role-permission catalogue entries are not edited by this API; this slice binds existing `Role`/`Team` rows only.
- Frontend visibility is still advisory: React maps `users.user.create`, `users.user.update`, and `users.user.disable` to prototype `manage_users`; Django remains authoritative.

Response examples for list, detail, assignment, `401`, `403`, validation failure, and last-admin lock-out are saved in `.ralph/runs/2026-07-04_131908_normal_run/api-response-examples.md`.

## Member Directory API (004A)

`GET /api/v1/members/`

Request headers:

```http
Authorization: Bearer <access_token>
X-Request-ID: req-members-list
```

Supported query parameters:
- `search` — matches member number, legal/display name, or folio number.
- `member_type` — `individual_farmer`, `fpc`, or `producer_institution`.
- `membership_status` — `active`, `inactive`, or `pending_verification`.
- `kyc_status` — `verified`, `missing`, `rekyc_due`, or `pending`.
- `default_status` — `no_default`, `existing_default`, or `past_default`.
- `page`, `page_size` — standard list pagination; `page_size` is capped at 100.

Success data uses the standard top-level list envelope from source §6.2. Each item contains:

```json
{
  "member_id": "uuid",
  "member_number": "MEM-00125",
  "member_type": "individual_farmer",
  "legal_name": "Ramesh Patil",
  "display_name": "Ramesh Patil",
  "folio_number": "FOL-456",
  "membership_status": "active",
  "kyc_status": "verified",
  "rekyc_due_date": "2027-06-22",
  "default_status": "no_default",
  "mobile_number": "******7890",
  "email": "ramesh@example.com",
  "share_summary": {
    "number_of_shares": 100,
    "holding_mode": "physical",
    "available_share_count": 100
  },
  "active_member_status": {
    "status": "active",
    "verified_at": "2026-06-22T10:30:00Z"
  }
}
```

Rules:
- Missing bearer token returns `401 AUTH_REQUIRED`; users without `members.member.read` return `403 FORBIDDEN`.
- Unknown query parameters or unsupported enum values return `400 VALIDATION_ERROR` with `field_errors`.
- The directory response never includes PAN or Aadhaar fields. `mobile_number` is masked to last four digits.
- Read-only list access writes no audit/workflow event. Exports, create/update, nominee, witness, KYC verification, share certificate, demat, land/crop, loan application, and Borrower 360 behavior are explicitly deferred.

## Member Profile Detail API (004B, extended by 004C)

`GET /api/v1/members/{member_id}/`

Rules:
- Requires a session-bound bearer token and `members.member.read`; missing auth returns
  `401 AUTH_REQUIRED`, missing permission returns `403 FORBIDDEN`, and a valid UUID that is
  unknown or soft-deleted returns `404 NOT_FOUND`.
- Returns the standard success envelope with member identifiers, status fields, masked mobile,
  registered address, share and active-member shell fields, `pan`/`aadhaar` as
  `{ "masked": "...", "can_view_full": boolean }`, nullable type-specific profile objects, and
  §44-shaped `available_actions[]`. `can_view_full` is true only for the matching field-specific
  reveal permission; it never includes the full source value in the profile response.
- `available_actions[]` is currently empty for member profile detail. The profile read does not infer
  `create_loan_application` from `membership_status`, `kyc_status`, `default_status`, or
  `applications.loan_application.create`; slice 005A and later eligibility slices own the
  source-backed loan-start action and blockers.
- For `member_type = individual_farmer`, `individual_profile` is either `null` when no row exists
  or contains `first_name`, nullable `middle_name`, `last_name`, nullable `gender`,
  `date_of_birth`, nullable `occupation`, `land_area_under_cultivation_acres`, `primary_crop`,
  `services_availed_flag`, and nullable `employment_or_service_years`.
- For `member_type = fpc` or `producer_institution`, `producer_institution_profile` is either
  `null` when no row exists or contains `institution_type`, nullable `registration_number`,
  `authorised_signatory_name`, `board_resolution_required_flag`, `services_availed_flag`, and
  nullable `produce_supply_years`. Decimal values are serialized as fixed two-decimal strings;
  dates are ISO `YYYY-MM-DD`.
- Profile persistence rejects an individual profile whose member is not `individual_farmer` and
  rejects a producer-institution profile whose member is not `fpc` or `producer_institution`.
- The response never serializes `pan_encrypted`, `aadhaar_encrypted`, `pan_hash`, `aadhaar_hash`, or
  full source values. Producer authorised-signatory PAN/Aadhaar fields are not stored or returned.
- Masked read-only profile access writes no workflow event and no profile-access audit row beyond
  normal authentication audit.

## Member Sensitive Reveal API (004I)

`POST /api/v1/members/{member_id}/reveal-sensitive-field/`

Request:

```json
{
  "field_name": "pan",
  "reason": "KYC verification during loan application"
}
```

Success response:

```json
{
  "success": true,
  "data": {
    "field_name": "pan",
    "value": "ABCDE1234F",
    "expires_at": "2026-06-22T10:35:00Z"
  },
  "meta": { "request_id": "req-id", "timestamp": "2026-06-22T10:30:00Z", "api_version": "v1" }
}
```

Rules:
- Implemented fields are member `pan` and `aadhaar` only. Nominee, witness, signatory, document,
  bank, export, and generic sensitive-data reveal remain deferred.
- Requires a session-bound bearer token, the base member read permission `members.member.read`, and
  the field-specific permission: `members.sensitive.reveal_pan` for `pan` and
  `members.sensitive.reveal_aadhaar` for `aadhaar`. Broad member read, KYC, document, admin, or
  export permissions do not grant reveal.
- Missing auth returns `401 AUTH_REQUIRED` without a reveal audit because no actor is known. Missing
  base read returns `403 FORBIDDEN`; missing field-specific permission returns
  `403 SENSITIVE_FIELD_ACCESS_DENIED`; unsupported/missing `field_name`, blank `reason`, or an
  unavailable source value return `400 VALIDATION_ERROR`; unknown or soft-deleted members return
  `404 NOT_FOUND`.
- Successful reveal returns the full value only in the immediate response with a five-minute
  `expires_at` timestamp. The response includes `Cache-Control: no-store` and `Pragma: no-cache`.
  The existing masked member profile remains masked; the frontend keeps full values only in
  temporary component state and clears the reason after success.
- Successful reveals write one `AuditLog` action `members.sensitive_field.revealed`. Authenticated
  denied reveal attempts write `members.sensitive_field.reveal_denied`. Audit metadata includes
  actor, member ID, field name, reason, outcome, denial reason when applicable, request ID, IP,
  user-agent, and expiry for successful reveals. Audit rows never include full PAN/Aadhaar,
  encrypted token columns, hash values, or submitted identifier-derived values.
- Sensitive reveal writes no `WorkflowEvent`.

## Loan Application Draft, Submit, and Reference API (005A-005C2)

`POST /api/v1/loan-applications/`

Request:

```json
{
  "member_id": "uuid",
  "nominee_id": "uuid",
  "required_loan_amount": "400000.00",
  "requested_tenure_months": 12,
  "declared_purpose": "Crop production loan for grape cultivation",
  "purpose_category": "crop_production",
  "loan_type_requested": "short_term",
  "land_holding_id": "uuid",
  "crop_plan_id": "uuid",
  "bank_account_id": "uuid",
  "cancelled_cheque_id": "uuid",
  "borrower_request_notes": "Assisted intake notes",
  "terms_acceptance_flag": false
}
```

`GET /api/v1/loan-applications/{loan_application_id}/`

`PATCH /api/v1/loan-applications/{loan_application_id}/`

Patch accepts only the draft facts above except `member_id`; borrower ownership is preserved.
`nominee_id` may be null while a draft is incomplete, but a supplied value must identify one
same-member nominee with adult age/date-of-birth evidence. Cross-member, unknown, minor, and
missing-age selections return `400 VALIDATION_ERROR` without application/audit/workflow changes.

Staff detail serializes `nominee` as metadata only: `nominee_id`, `nominee_name`, nullable
`age_at_application`, `minor_flag`, `kyc_status`, nullable `relationship_to_borrower`,
and `signature_required_flag`. It never includes PAN/Aadhaar values,
tokens, hashes, or reveal controls.

Staff list/detail return `assigned_owner: null` until an assignment/task owner is persisted by its
owning future slice. `received_by_user` and `created_by_user` remain intake/audit facts and are never
projected as assignment facts. Detail also returns §44-shaped `available_actions[]`. The currently implemented
detail action is `submit`: it is returned only to an object-scoped actor with
`applications.loan_application.submit` while the application is a draft, and its `enabled` /
`disabled_reason` fields reflect whether the persisted submit facts are complete. Submitted and
later-stage applications return an empty action list until their owning workflow APIs supply
actions. Documentation, sanction, security, SAP, and disbursement facts remain absent rather than
being inferred by the detail response or frontend.

`POST /api/v1/loan-applications/{loan_application_id}/submit/`

Request body is accepted as a JSON object. A stored adult `nominee_id` is required. `submission_notes` may be supplied by clients, but 005B
does not persist notes because no source-backed column exists yet.

`POST /api/v1/loan-applications/{loan_application_id}/generate-reference/`

Request body is accepted as a JSON object. In 005C this endpoint represents the successful
completeness-pass transition only; it requires the stored nominee selection but does not evaluate document checklist items,
deficiencies, eligibility, appraisal, sanction, or disbursement.

`GET /api/v1/loan-applications/{loan_application_id}/completeness-check/`

Returns the derived completeness workbench for a submitted application:

```json
{
  "loan_application_id": "uuid",
  "application_reference_number": null,
  "application_status": "submitted",
  "current_stage": "initial_loan_request",
  "completeness_status": "not_started",
  "member": {
    "member_id": "uuid",
    "display_name": "Ramesh Patil",
    "member_type": "individual_farmer",
    "folio_number": "FOL-005A"
  },
  "nominee": {
    "nominee_id": "uuid",
    "nominee_name": "Sita Patil",
    "age_at_application": 42,
    "minor_flag": false,
    "kyc_status": "verified",
    "relationship_to_borrower": "Spouse",
    "signature_required_flag": true
  },
  "nominee_selection_status": "valid",
  "required_checklist_items": [
    {
      "document_type": "borrower_pan",
      "required_flag": true,
      "submission_status": "submitted",
      "verification_status": "rejected",
      "latest_application_document_id": "uuid",
      "latest_version_number": 2,
      "complete": false,
      "reason_code": "not_verified"
    },
    {
      "document_type": "crop_plan",
      "required_flag": true,
      "submission_status": "pending",
      "verification_status": "pending",
      "latest_application_document_id": null,
      "latest_version_number": null,
      "complete": false,
      "reason_code": "missing_metadata"
    }
  ],
  "blocking_document_types": ["borrower_pan", "crop_plan"],
  "can_generate_reference": false,
  "available_actions": [
    {
      "action_code": "pass_completeness",
      "label": "Generate reference number",
      "enabled": false,
      "disabled_reason": "Required nominee and document checks must be complete.",
      "required_permission": "applications.loan_application.complete_check",
      "required_role": "deputy_manager_finance"
    }
  ]
}
```

`POST /api/v1/loan-applications/{loan_application_id}/completeness-check/pass/`

Request body is accepted as a JSON object. On success the endpoint returns the canonical serialized
loan application after calling `generate_reference_after_completeness_pass(...)`, including the
generated `LO...` reference and `loan_request_register_entry` summary.

`POST /api/v1/loan-applications/{loan_application_id}/return-with-deficiencies/`

Request:

```json
{
  "communication_mode": "email",
  "message": "Please submit corrected documents to proceed.",
  "items": [
    {
      "item_code": "borrower_pan",
      "remarks": "PAN name does not match the member profile."
    }
  ]
}
```

005F uses `items[].item_code` to select source-backed blocking facts from the 005E completeness
workbench. The source §19.7 example uses `deficiency_ids`, but prior slices did not create
deficiency rows before the return action; A-040 records this request-shape decision.

Success data:

```json
{
  "loan_application_id": "uuid",
  "application_reference_number": null,
  "application_status": "incomplete_returned",
  "current_stage": "initial_loan_request",
  "completeness_status": "incomplete",
  "communication_mode": "email",
  "message": "Please submit corrected documents to proceed.",
  "items": [
    {
      "deficiency_id": "uuid",
      "loan_application_id": "uuid",
      "item_code": "borrower_pan",
      "deficiency_type": "not_verified",
      "source_reason_code": "not_verified",
      "description": "borrower pan is submitted but not verified.",
      "remarks": "PAN name does not match the member profile.",
      "resolution_status": "open",
      "raised_by_user_id": "uuid",
      "raised_at": "2026-07-09T15:30:00Z",
      "resolved_by_user_id": null,
      "resolved_at": null,
      "resolution_notes": ""
    }
  ]
}
```

`GET /api/v1/loan-applications/{loan_application_id}/deficiencies/`

Returns `{ "loan_application_id": "uuid", "items": [...], "available_actions": [...] }` using
the deficiency item shape above and the same completeness resource-action projection as the
completeness read.

`POST /api/v1/deficiencies/{deficiency_id}/resolve/`

Request:

```json
{
  "resolution_notes": "Nominee Aadhaar uploaded and verified."
}
```

Success returns the resolved deficiency item with `resolution_status = resolved`, resolver actor,
and `resolved_at`.

`POST /api/v1/loan-applications/{loan_application_id}/rejection-note/`

Request:

```json
{
  "rejection_stage": "credit_assessment",
  "rejection_reason_category": "eligibility",
  "detailed_reason": "Borrower does not meet active member criteria.",
  "reapply_allowed_flag": true,
  "communication_mode": "email"
}
```

Success data:

```json
{
  "rejection_note_id": "uuid",
  "loan_application_id": "uuid",
  "rejection_stage": "credit_assessment",
  "rejection_reason_category": "eligibility",
  "detailed_reason": "Borrower does not meet active member criteria.",
  "reapply_allowed_flag": true,
  "note_status": "draft",
  "communication_status": "not_sent",
  "prepared_by_user_id": "uuid",
  "approved_by_user_id": null,
  "communication_mode": "email",
  "communication_id": null,
  "sent_by_user_id": null,
  "sent_at": null,
  "created_at": "2026-07-10T01:57:23Z",
  "updated_at": "2026-07-10T01:57:23Z",
  "updated_by_user_id": "uuid"
}
```

`POST /api/v1/rejection-notes/{rejection_note_id}/send/`

Request:

```json
{
  "recipient_email": "borrower@example.com",
  "message_override": null
}
```

Success returns the rejection note shape above with `note_status = sent`,
`communication_status = sent`, `sent_by_user_id`, and `sent_at` populated. The derived
`communication_status` is `not_sent` while `sent_at` is null. The send endpoint is a
metadata/status transition only in 005H; it does not call a real email/SMS/courier provider and
does not create a `communications` row.

Rules:
- All endpoints require session-bound bearer authentication.
- `POST` requires `applications.loan_application.create`; `GET` requires
  `applications.loan_application.read`; `PATCH` requires
  `applications.loan_application.update`; submit requires
  `applications.loan_application.submit`; reference generation requires
  `applications.loan_application.complete_check`.
- Detail, patch, submit, and reference-generation endpoints also enforce object access after the
  global permission check and after `404` lookup. Created/received users can access their
  applications; Credit Manager access is explicitly limited to applications already in the
  `credit_assessment` stage. A same-permission actor outside those scopes receives
  `403 OBJECT_ACCESS_DENIED`.
- 005A stores draft applications. 005B permits only `draft -> submitted`.
  `current_stage` remains `initial_loan_request`, `completeness_status` remains
  `not_started`, and submitted applications are locked from `PATCH`.
- `application_reference_number` remains nullable through submit. 005C generates the formal
  `LO...` number only from the submitted state at the source-backed completeness-pass point,
  using the `loan_application_reference` system sequence (`LO` prefix, 8-digit padding, starting
  at `LO00000001`). On success it sets `application_status = reference_generated`,
  `current_stage = credit_assessment`, and `completeness_status = complete`.
- 005E makes the source-backed completeness pass explicit. Workbench read requires
  `applications.loan_application.read`; pass requires
  `applications.loan_application.complete_check`. Both endpoints reuse the application object-access
  boundary after global permission and `404` checks.
- 005E2 wires the staff Completeness Workbench to the list, document-checklist,
  completeness-check, deficiency, and rejection-note APIs with no mock fallback. Submitted and
  `incomplete_returned` queue rows are requested as separate status-filtered list reads. 005E4
  completes the six-field §44 `available_actions` on completeness and deficiency reads. Pass,
  return, resolve, and rejection-note creation respectively require
  `applications.loan_application.complete_check`,
  `applications.loan_application.return_deficiency`, `applications.deficiency.resolve`, and
  `applications.rejection_note.create`; each projection and write boundary uses the same
  application object scope and state/resource predicate. The UI intersects that projection with
  `/auth/me` only for usability and never infers resource authority. Pass sends `{}`; return sends only
  `communication_mode`, `message`, and current blocker `items[{item_code, remarks?}]`; deficiency
  resolution sends only `resolution_notes`; rejection-note creation sends the exact 005H draft
  fields. Every successful action re-reads the canonical queue, document checklist, completeness,
  and full deficiency history. A `409` is not retried and refresh occurs only after an explicit
  user choice.
- The pass endpoint first enforces submitted/non-duplicate state and returns
  `409 INVALID_STATE_TRANSITION` for draft, already-reference-generated, or register-existing
  applications. It then evaluates the latest 005D metadata row for each mandatory application-stage
  document code and requires `submission_status = submitted` plus
  `verification_status = verified`. Missing latest metadata returns `reason_code =
  missing_metadata`; submitted but pending/rejected latest metadata returns `reason_code =
  not_verified`. Validation failures return `400 VALIDATION_ERROR` with item-level
  `required_checklist_items` and create no sequence/register/audit/workflow side effects.
- Return-with-deficiencies requires `applications.loan_application.return_deficiency`; deficiency
  list requires `applications.loan_application.read`; deficiency resolve requires
  `applications.deficiency.resolve`. All reuse
  `applications.services.evaluate_application_object_access(...)` after global permission and
  `404` checks.
- Rejection-note creation requires `applications.rejection_note.create`; the separate send shell
  retains its existing send boundary pending its owning workflow work. Both endpoints reuse the
  application object-access boundary after global permission and `404` checks. Borrower portal
  tokens have only portal own-data permissions and receive `403 FORBIDDEN` on staff
  rejection-note routes; suspended portal sessions receive `401 INVALID_TOKEN` before any
  rejection-note side effect.
- Return-with-deficiencies is limited to submitted applications that do not yet have an
  `LO...` reference and do not have a loan request register entry. Draft, already-returned
  `incomplete_returned`, and reference-generated attempts return `409 INVALID_STATE_TRANSITION`;
  A-041 records the blocked repeat-return assumption because source docs do not define a repeat
  return rule.
- Return items must match current blocking 005E completeness facts. `missing_metadata` source facts
  become `deficiency_type = missing_document`; `not_verified` source facts become
  `deficiency_type = not_verified`. Empty selections, duplicate item codes, arbitrary item codes,
  missing communication mode/message, or unknown fields return `400 VALIDATION_ERROR`.
- Successful return-with-deficiencies sets `application_status = incomplete_returned`, keeps
  `current_stage = initial_loan_request`, sets `completeness_status = incomplete`, creates open
  `deficiencies` rows, writes
  `applications.loan_application.returned_with_deficiencies` audit metadata, and records a
  `loan_application` workflow event from submitted to incomplete_returned with trigger reason
  "Application returned with completeness deficiencies." It does not generate a reference, create a
  loan request register row, advance to credit assessment, or visibly advance the sequence.
- Deficiency resolve closes only open rows and writes `applications.deficiency.resolved` audit
  metadata plus an `application_deficiency` workflow event from open to resolved. Borrower portal
  re-upload, borrower response drafting, application resubmission, rejection notes, and
  communications delivery are deferred to later slices.
- Rejection-note creation is limited to submitted applications without an `LO...` reference, loan
  request register entry, or existing rejection note. Draft, already-returned
  `incomplete_returned`, reference-generated, and duplicate-create attempts return
  `409 INVALID_STATE_TRANSITION` and create no rejection note, success audit row, workflow event,
  reference, register row, or sequence advancement.
- Rejection-note payload validation requires `rejection_stage`, `rejection_reason_category`,
  nonblank `detailed_reason`, boolean `reapply_allowed_flag` when supplied, and
  `communication_mode`; unknown fields return `400 VALIDATION_ERROR`. Supported stages are
  `completeness`, `credit_assessment`, and `sanction_committee`. Supported reason categories are
  `missing_document`, `eligibility`, `default`, `purpose_mismatch`, `limit_issue`,
  `committee_rejection`, and `other`. Supported communication modes are `email`, `courier`,
  `hard_copy`, and `sms_summary`.
- Successful rejection-note creation writes one `rejection_notes` row with `note_status = draft`,
  writes `applications.rejection_note.created` metadata-only audit, and records a
  `rejection_note` workflow event into `draft`. It does not change `loan_applications` status in
  005H because the current source-backed status vocabulary lacks a generic intake rejection state;
  A-045 records this deferral.
- Send requires an existing draft rejection note and a nonblank `recipient_email`. Unknown send
  fields return `400 VALIDATION_ERROR`; duplicate send attempts return `400 VALIDATION_ERROR` with
  no second audit/workflow event. Successful send stamps `sent_by_user_id` and `sent_at`, writes
  `applications.rejection_note.sent` metadata-only audit, and records a `rejection_note` workflow
  event from `draft` to `sent`.
- Required draft validation is intentionally narrow: known borrower member,
  well-formed UUID references, subresource references owned by the borrower
  member, and positive requested amount when supplied.
- Draft saves allow incomplete KYC/documents. 005B submit requires the
  source-backed request facts already persisted by 005A: borrower member,
  positive `required_loan_amount`, nonblank `declared_purpose`, and nonblank
  `purpose_category`. Nominee, application-document placeholder, completeness,
  and deficiency gates remain future slices.
- Responses include member identity summaries plus land/crop and masked
  bank/cancelled-cheque metadata by ID. They never include PAN, Aadhaar, full
  bank account numbers, encrypted values, protected tokens, or hash fields.
  005B responses additionally include nullable `submitted_at` and
  `submitted_by_user_id`. 005C responses additionally include nullable
  `loan_request_register_entry` metadata sourced from the application/member record:
  register entry ID, loan application ID, reference number, member ID, received/reference dates,
  received channel, register status, borrower name, folio, member type, requested amount,
  purpose category, current stage, owner role, and pending downstream statuses.
- 005I2 staff detail responses additionally include `rejection_note`, either `null` or a
  metadata-only summary with `rejection_note_id`, `note_status`, `rejection_stage`,
  `rejection_reason_category`, `reapply_allowed_flag`, prepared/approved/sent actor IDs,
  timestamps, `communication_mode`, and nullable `communication_id`. Staff detail does not include
  rejection-note `detailed_reason`, does not change `application_status`, and read-only detail
  access writes no success audit/workflow event. Borrower portal application routes continue to
  omit staff rejection-note metadata.
- Successful create writes `applications.loan_application.created` audit metadata
  plus one `loan_application` workflow event into `draft`. Successful patch
  writes `applications.loan_application.updated` audit metadata and does not
  create a workflow event because no source-backed state transition occurs.
  Successful submit writes `applications.loan_application.submitted` audit
  metadata plus one `loan_application` workflow event from `draft` to
  `submitted`. Successful reference generation writes
  `applications.loan_application.reference_generated` audit metadata plus one
  `loan_application` workflow event from `submitted` to `reference_generated`.
- Unknown applications return `404 NOT_FOUND`; missing global permissions return
  `403 FORBIDDEN`; object-scope mismatches return `403 OBJECT_ACCESS_DENIED`; invalid submit
  facts return `400 VALIDATION_ERROR`; re-submit, other non-draft submit, draft reference generation,
  or duplicate reference attempts return `409 INVALID_STATE_TRANSITION`. Object-access denials do
  not write success audit rows, workflow events, register rows, application references, or visible
  sequence advancement. Return-with-deficiencies permission/object denials additionally create no
  deficiency rows and no deficiency success audit/workflow events. Rejection-note permission/object
  denials additionally create no rejection-note rows and no rejection-note success audit/workflow
  events.

## Application Document and Checklist API (005D)

`GET /api/v1/loan-applications/{loan_application_id}/application-documents/`

Returns:

```json
{
  "loan_application_id": "uuid",
  "items": [
    {
      "application_document_id": "uuid",
      "loan_application_id": "uuid",
      "document_type": "borrower_pan",
      "party_type": "borrower",
      "party_id": "uuid",
      "document_file": {
        "document_id": "uuid",
        "file_name": "borrower-pan.pdf",
        "mime_type": "application/pdf",
        "file_size_bytes": 256,
        "sensitivity_level": "restricted",
        "uploaded_at": "2026-07-09T14:00:00Z"
      },
      "required_flag": true,
      "submission_status": "submitted",
      "verification_status": "pending",
      "verified_by_user_id": null,
      "verified_at": null,
      "remarks": "PAN copy received at branch.",
      "version_number": 1,
      "created_at": "2026-07-09T14:00:00Z",
      "created_by_user_id": "uuid",
      "updated_at": "2026-07-09T14:00:00Z",
      "updated_by_user_id": "uuid"
    }
  ]
}
```

`POST /api/v1/loan-applications/{loan_application_id}/application-documents/`

Request:

```json
{
  "document_type": "borrower_pan",
  "party_type": "borrower",
  "party_id": "uuid",
  "document_file_id": "uuid",
  "remarks": "PAN copy received at branch."
}
```

`POST /api/v1/application-documents/{application_document_id}/verify/`

Request:

```json
{
  "verification_status": "verified",
  "remarks": "PAN name matches member profile."
}
```

`GET /api/v1/loan-applications/{loan_application_id}/document-checklist/`

`POST /api/v1/loan-applications/{loan_application_id}/document-checklist/refresh/`

Checklist responses contain the source-required item codes with pending placeholders until metadata
exists: `loan_application_form`, `borrower_pan`, `borrower_aadhaar_ovd`, `nominee_pan`,
`nominee_aadhaar_ovd`, `share_certificate_copy`, `land_document_7_12`, `crop_plan`, and
`six_month_bank_statement`.

Rules:
- All endpoints require session-bound bearer authentication.
- Application-document list and checklist read/refresh require
  `applications.loan_application.read`. Upload requires `applications.document.upload`. Verify
  requires `applications.document.verify`.
- Application-scoped endpoints return `404 NOT_FOUND` for unknown applications before object-scope
  checks, then use `applications.services.evaluate_application_object_access(...)`. Same-permission
  actors outside the application scope receive `403 OBJECT_ACCESS_DENIED`; missing global permission
  returns `403 FORBIDDEN`.
- Upload links metadata to an existing `documents.DocumentFile` by `document_file_id`; 005D does not
  upload or duplicate file bytes. Upload is accepted only after application submit and creates a new
  version row for duplicate document type/party combinations instead of overwriting prior history.
- Supported `party_type` values are `borrower`, `nominee`, and `witness`. Supported verification
  values are `pending`, `verified`, and `rejected`.
- Successful upload writes `applications.application_document.attached`; successful verification
  writes `applications.application_document.verified`. Both audit rows are metadata-only and never
  include raw file bytes, storage keys, checksums, PAN, Aadhaar, full bank-account numbers, encrypted
  token values, or hashes.
- Checklist refresh is currently a derived read operation under A-039 because the source names the
  endpoint but no exact checklist-refresh mutation or permission is defined yet. It writes no audit
  or workflow event.

## Member Bank Account and Cancelled Cheque Metadata API (004J)

`GET /api/v1/members/{member_id}/bank-accounts/`

Rules:
- Requires a session-bound bearer token and `members.member.read` under A-034; missing auth returns
  `401 AUTH_REQUIRED`, missing permission returns `403 FORBIDDEN`, and an unknown or
  soft-deleted member returns `404 NOT_FOUND`.
- Returns the standard top-level list envelope. Each item contains `bank_account_id`,
  `owner_party_type`, `owner_party_id`, `account_holder_name`, masked `account_number` as
  `{ "masked": "...", "last4": "...", "can_view_full": false }`, `ifsc`, nullable `bank_name`,
  nullable `branch_name`, `verification_status`, nullable `cancelled_cheque_id`, nullable
  `signature_verified_flag`, `status`, and `created_at`.
- The response never serializes full account numbers, `account_number_encrypted`, or
  `account_number_hash`.

`POST /api/v1/members/{member_id}/bank-accounts/`

Request:

```json
{
  "account_holder_name": "Ramesh Patil",
  "account_number": "123456789012",
  "ifsc": "HDFC0001234",
  "bank_name": "HDFC Bank",
  "branch_name": "Nashik Road",
  "verification_status": "pending",
  "cancelled_cheque_id": null,
  "signature_verified_flag": null,
  "status": "active"
}
```

Rules:
- Requires `members.member.update` under A-034.
- Account holder name, account number, and IFSC are required. Account numbers must contain at least
  four digits. `verification_status` is limited to `pending`, `verified`, or `rejected`; `status` is
  limited to `active` or `inactive`; malformed `cancelled_cheque_id` returns
  `400 VALIDATION_ERROR`.
- The stored row keeps only a protected token, keyed hash, and last four digits for the account
  number. The create response is masked and `can_view_full` is always false.
- Successful create writes `members.bank_account.created` audit metadata with member ID,
  bank-account ID, masked last four, IFSC, verification status, signature flag, status, request/IP,
  and user-agent. Audit metadata never includes full account numbers, protected tokens, hashes,
  cheque images, or file bytes.

`GET /api/v1/members/{member_id}/cancelled-cheques/`

Rules:
- Requires `members.member.read` under A-034.
- Returns the standard top-level list envelope. Each item contains `cancelled_cheque_id`,
  nullable `loan_application_id`, `member_id`, `document_id`, masked `account_number` as
  `{ "masked": "...", "last4": "...", "can_view_full": false }`, `ifsc`, nullable
  `branch_name`, `verification_status`, `signature_mismatch_flag`, and `created_at`.
- Full account numbers, protected token values, and hashes are never serialized.

`POST /api/v1/members/{member_id}/cancelled-cheques/`

Request:

```json
{
  "loan_application_id": null,
  "document_id": "uuid",
  "account_number": "987654324321",
  "ifsc": "SBIN0000456",
  "branch_name": "Lasalgaon",
  "verification_status": "pending",
  "signature_mismatch_flag": false
}
```

Rules:
- Requires `members.member.update` under A-034.
- `document_id`, account number, and IFSC are required. `loan_application_id` is accepted only as a
  nullable UUID placeholder because real loan applications do not exist yet. `verification_status`
  is limited to `pending`, `verified`, or `rejected`.
- Successful create writes `members.cancelled_cheque.created` audit metadata with member ID,
  cheque ID, nullable loan application ID, document ID, masked last four, IFSC, verification status,
  signature mismatch flag, request/IP, and user-agent.
- Read/list endpoints write no audit row and no workflow event. Create endpoints write no workflow
  event.
- Explicit deferrals: duplicate-active-borrower warnings, bank verification letters, signature
  mismatch resolution, blank-dated cheque custody, payment initiation, disbursement readiness gates,
  bank-account full reveal, and Member Profile/Borrower360 UI wiring.

## Member Nominee API (004D)

`GET /api/v1/members/{member_id}/nominees/`

Rules:
- Requires a session-bound bearer token and `members.nominee.read`; missing auth returns
  `401 AUTH_REQUIRED`, missing permission returns `403 FORBIDDEN`, and an unknown or
  soft-deleted member returns `404 NOT_FOUND`.
- Returns the standard top-level list envelope. Each nominee item contains `nominee_id`,
  `nominee_name`, nullable `date_of_birth`, `age_at_application`, `gender`, nullable
  `relationship_to_borrower`, masked `pan`/`aadhaar` as `{ "masked": "...", "can_view_full": false }`,
  `kyc_status`, `minor_flag`, `signature_required_flag`, and `created_at`.
- Read-only nominee access writes no workflow event and no nominee-access audit row.

`POST /api/v1/members/{member_id}/nominees/`

Request data:

```json
{
  "nominee_name": "Sita Patil",
  "date_of_birth": "1985-05-20",
  "gender": "female",
  "relationship_to_borrower": "Spouse",
  "pan": "ABCDE1234F",
  "aadhaar": "123412341234",
  "signature_required_flag": true
}
```

Rules:
- Requires `members.nominee.create`, not `members.nominee.read`.
- Persists member-level nominees only. `loan_application_id` exists as nullable storage for a future
  application snapshot but is not accepted or populated by the 004D API.
- PAN and Aadhaar are required. Missing values return `400 MISSING_REQUIRED_FIELD`; invalid source
  formats return `400 INVALID_PAN_FORMAT` or `400 INVALID_AADHAAR_FORMAT`.
- Nominees below legal majority return `400 NOMINEE_MINOR_NOT_ALLOWED`; 004D uses age 18 per A-031.
- Stored identity values use protected tokens plus keyed hashes. Responses and audit logs never
  include full PAN/Aadhaar, `pan_encrypted`, `aadhaar_encrypted`, `pan_hash`, `aadhaar_hash`, or
  values derived from submitted PAN/Aadhaar identifiers.
- Successful creation returns the nominee item in the standard success envelope, sets
  `kyc_status: "pending"`, `minor_flag: false`, stores the calculated `age_at_application`, and
  writes `members.nominee.created` audit metadata without a workflow event.

## Member Shareholding API (004F)

`GET /api/v1/members/{member_id}/shareholdings/`

Rules:
- Requires a session-bound bearer token and `members.shareholding.read`; missing auth returns
  `401 AUTH_REQUIRED`, missing permission returns `403 FORBIDDEN`, and an unknown or
  soft-deleted member returns `404 NOT_FOUND`.
- Returns the standard top-level list envelope. Each item contains `shareholding_id`,
  `folio_number`, `number_of_shares`, `holding_mode`, nullable `valuation_per_share`, nullable
  `valuation_effective_date`, `pledged_share_count`, `available_share_count`,
  `future_shares_pledge_flag`, and `status`.
- Read-only shareholding access writes no workflow event and no access audit row.

`POST /api/v1/members/{member_id}/shareholdings/`

Request data:

```json
{
  "folio_number": "FOL-456",
  "number_of_shares": 100,
  "holding_mode": "physical",
  "valuation_per_share": "2000.00",
  "valuation_effective_date": "2026-04-01",
  "pledged_share_count": 15,
  "future_shares_pledge_flag": true
}
```

Rules:
- Requires `members.shareholding.create`, not `members.shareholding.read`.
- `holding_mode` is limited to `physical`, `demat`, or `mixed`. Demat account and latest valuation
  references are accepted as nullable UUID fields only when supplied; demat account table behavior
  remains deferred.
- `number_of_shares` and `pledged_share_count` must be non-negative integers, and pledged shares
  cannot exceed total shares. `available_share_count` is maintained as
  `number_of_shares - pledged_share_count` and protected by a database check constraint.
- Successful create updates the member directory/profile share summary from active shareholdings:
  total shares, total available shares, and holding mode (`mixed` when multiple active modes exist).
- Successful create writes `members.shareholding.created` audit metadata without a workflow event.
- `PATCH /api/v1/shareholdings/{shareholding_id}/`, share certificates, demat account management,
  CDSL integration, share valuation calculation, pledge eligibility, and loan-limit rules are
  deferred to later slices.

## Member Land Holding and Crop Plan API (004G)

`GET /api/v1/members/{member_id}/land-holdings/`

Rules:
- Requires a session-bound bearer token and `members.member.read` per A-032; missing auth returns
  `401 AUTH_REQUIRED`, missing permission returns `403 FORBIDDEN`, and an unknown or
  soft-deleted member returns `404 NOT_FOUND`.
- Returns the standard top-level list envelope. Each item contains `land_holding_id`,
  `document_type`, nullable location/survey fields, `area_acres`, `document_id`,
  `verification_status`, nullable verifier/timestamp fields, and `created_at`.
- Read-only list access writes no workflow event and no access audit row.

`POST /api/v1/members/{member_id}/land-holdings/`

Request data:

```json
{
  "document_type": "7_12_extract",
  "survey_number": "123/4",
  "village": "Village Name",
  "taluka": "Niphad",
  "district": "Nashik",
  "state": "Maharashtra",
  "area_acres": "5.00",
  "document_id": "uuid"
}
```

Rules:
- Requires `members.member.update` per A-032.
- `document_type`, positive `area_acres`, and valid non-null `document_id` are required.
- Successful create sets `verification_status: "pending"` and writes
  `members.land_holding.created` audit metadata without a workflow event.

`GET /api/v1/members/{member_id}/crop-plans/`

Rules:
- Requires a session-bound bearer token and `members.member.read` per A-032.
- Returns the standard top-level list envelope. Each item contains `crop_plan_id`,
  nullable `loan_application_id`, `crop_type`, nullable `season`, `planned_area_acres`,
  nullable `estimated_cost_amount`, `loan_purpose_alignment`, nullable `document_id`,
  `verification_status`, nullable verifier/timestamp fields, and `created_at`.
- Read-only list access writes no workflow event and no access audit row.

`POST /api/v1/members/{member_id}/crop-plans/`

Request data:

```json
{
  "loan_application_id": "uuid",
  "crop_type": "grapes",
  "season": "FY2026 Kharif",
  "planned_area_acres": "5.00",
  "estimated_cost_amount": "100000.00",
  "loan_purpose_alignment": "agriculture_aligned",
  "document_id": "uuid"
}
```

Rules:
- Requires `members.member.update` per A-032.
- `crop_type`, positive `planned_area_acres`, and `loan_purpose_alignment` are required.
- `loan_application_id` and `document_id` are optional, but malformed UUIDs are rejected.
- Successful create sets `verification_status: "pending"` and writes
  `members.crop_plan.created` audit metadata without a workflow event.
- Detail/update endpoints, verification actions, loan-limit calculations, scale-of-finance,
  eligibility blockers, and purpose decisions are deferred to later application/eligibility slices.

## Member KYC Profile and Document API (004H)

`GET /api/v1/kyc-profiles/?party_type=member&party_id={member_id}`

Rules:
- Requires a session-bound bearer token and `kyc.profile.read`.
- 004H supports `party_type=member` only. Unknown or soft-deleted members return `404 NOT_FOUND`.
- Success returns one profile object with status, CKYC consent, beneficial-ownership flag, risk
  rating, last verification fields, re-KYC due date, rejection reason, and embedded KYC document
  metadata. `ckyc_identifier_encrypted` and sensitive identity values are never serialized.

`POST /api/v1/kyc-profiles/` and `PATCH /api/v1/kyc-profiles/{kyc_profile_id}/`

Rules:
- Create requires `kyc.profile.create`; patch requires `kyc.profile.update`.
- Create requires `party_type`, `party_id`, and `ckyc_consent_flag`; risk rating is limited to
  `low`, `medium`, or `high`.
- Duplicate member-party create requests return `400 VALIDATION_ERROR` with `party_id:
  "A KYC profile already exists for this member."`; clients should use
  `GET /api/v1/kyc-profiles/?party_type=member&party_id={member_id}` to read the existing profile
  and `PATCH /api/v1/kyc-profiles/{kyc_profile_id}/` to update it.
- Successful create/update writes `kyc.profile.created` / `kyc.profile.updated` audit metadata only.

`POST /api/v1/kyc-profiles/{kyc_profile_id}/documents/`

Multipart fields: `document_type`, `file`, `self_attested_flag`.

Rules:
- Requires `kyc.document.upload`.
- `document_type` is limited to `pan`, `aadhaar`, `photo`, and `ckyc_consent`.
- PAN and Aadhaar require `self_attested_flag=true`.
- The uploaded file is stored as a restricted `document_files` row and returned through KYC document
  metadata only; no document download endpoint is added by 004H.
- Successful upload writes `kyc.document.uploaded` audit metadata and no workflow event.

`POST /api/v1/kyc-documents/{kyc_document_id}/verify/`

Rules:
- Requires `kyc.document.verify`.
- `verification_status` is limited to `verified` or `rejected`; remarks are optional metadata.
- Successful verification updates the KYC document verifier/timestamp and, per A-033, updates the
  profile/member KYC status and a two-year re-KYC due date for verified results.
- Successful verification writes `kyc.document.verified` audit metadata only. Audit rows exclude
  PAN/Aadhaar plaintext, identity hashes, encrypted CKYC identifiers, and file bytes.
- Re-KYC review endpoints (§18.5), KYC deficiencies, sensitive reveal, CKYC provider integration,
  appraisal/disbursement blockers, and nominee/witness/signatory KYC remain deferred.

## Shared response envelope (002C2)

Health and auth endpoints use one production envelope implementation in `sfpcl_credit/api.py`
(`success_response`, `error_response`, `response_meta`). All success and error responses expose the
same `meta` keys — `request_id`, `timestamp`, `api_version` — matching `docs/source/api-contracts.md`
§6.1/§6.4. Auth token/session/audit behavior now lives behind explicit module functions in
`sfpcl_credit/identity/modules/` (`tokens.py`, `auth_service.py`); views only parse HTTP, call the
module, and translate known errors. `auth_service.validate_access_session` is the session-bound
validator used by `GET /api/v1/auth/me/`, resolving A-008 for current-user reads: a logged-out,
revoked, expired-session, or inactive-user access token cannot retrieve profile or permission data.

## Current user response (002D3)

`GET /api/v1/auth/me/`

Request headers:

```http
Authorization: Bearer <access_token>
X-Request-ID: req-me-001
```

Success data:

```json
{
  "user_id": "uuid",
  "full_name": "Credit Manager",
  "email": "credit.manager@sfpcl.example",
  "mobile_number": "+919999999999",
  "status": "active",
  "roles": [
    {
      "role_code": "credit_manager",
      "role_name": "Credit Manager"
    }
  ],
  "teams": [
    {
      "team_code": "credit_assessment",
      "team_name": "Credit Assessment"
    }
  ],
  "role_codes": ["credit_manager"],
  "team_codes": ["credit_assessment"],
  "permissions": ["approvals.case.create", "credit.appraisal.review"],
  "available_actions": ["approvals.case.create", "credit.appraisal.review"]
}
```

Rules:
- `permissions` are sorted, de-duplicated `RolePermission.permission.permission_code` values for the user's active primary role.
- `roles` contains the active primary role as `{ role_code, role_name }`; inactive primary roles return empty `roles`, empty `role_codes`, and empty `permissions`.
- `teams` contains active memberships to active teams as `{ team_code, team_name }`, sorted by `team_code`; inactive memberships and inactive teams are excluded.
- `role_codes` and `team_codes` are additive compatibility fields derived from `roles` and `teams`.
- Roles with no seeded production permission links, including the A-007 `sales_team_user` and `it_head` cases, return an empty permission list until source documents define grants. A-023 gives `management_viewer` the source-backed `management_readonly` dashboard scope. The guarded local/demo `seed_demo_users` command keeps a neutral `demo.zero@sfpcl.example` user on `it_head`; its narrow A-011 exception creates the local/dev-only `local_demo_tracer_user` role and grants that role exactly `tracer.lifecycle.run` for `demo.tracer@sfpcl.example`.
- `available_actions` currently mirrors effective permission codes; later workflow/object-level slices may narrow it per resource while backend enforcement remains authoritative.
- 002D3 corrected the architecture-review gap by matching `docs/source/api-contracts.md` §11.4 before 002E frontend route-shell wiring consumes `/auth/me/`.
- 002E maps canonical backend permission codes to the existing prototype `can(...)` permission names only for currently implemented UI affordances. Unmapped backend codes do not grant frontend visibility; backend enforcement remains authoritative and future slices should extend the mapping when they add screens/actions.

## Audit log read (003A)

`GET /api/v1/audit-logs/`

Read-only, protected endpoint over the existing append-only `identity.AuditLog` model
(`docs/source/api-contracts.md` §42.1). Serialization, filtering, and pagination live behind
`sfpcl_credit/identity/modules/audit_log.py`; `sfpcl_credit/identity/audit_views.py` is a thin
`require_GET` view. No update/delete endpoint exists; the read creates no audit row.

Request headers:

```http
Authorization: Bearer <access_token>
X-Request-ID: req-audit-list
```

Query parameters (all optional):
- `entity_type` — free-text exact match on `AuditLog.entity_type`.
- `entity_id` — UUID; invalid UUID returns `400 VALIDATION_ERROR` with `field_errors.entity_id`.
- `actor_user_id` — UUID; invalid UUID returns `400 VALIDATION_ERROR` with `field_errors.actor_user_id`.
- `page`, `page_size` — standard top-level pagination (default `page_size` 20, max 100).
- Any other query parameter returns `400 VALIDATION_ERROR` with the unknown key in `field_errors`.

Success (top-level `pagination` envelope, newest-first by `created_at`):

```json
{
  "success": true,
  "data": [
    {
      "audit_log_id": "uuid",
      "actor": { "user_id": "uuid", "full_name": "Ivy Auditor" },
      "actor_type": "user",
      "action": "loan_application.submitted",
      "entity_type": "loan_application",
      "entity_id": "uuid",
      "old_value": { "application_status": "draft" },
      "new_value": { "application_status": "submitted" },
      "ip_address": "10.0.0.1",
      "created_at": "2026-06-22T10:30:00Z"
    }
  ],
  "pagination": { "page": 1, "page_size": 20, "total_count": 1, "total_pages": 1, "has_next": false, "has_previous": false },
  "meta": { "request_id": "req-audit-list", "timestamp": "…Z", "api_version": "v1" }
}
```

Rules:
- Permission: `audit.audit_log.read` (002C catalogue; held by `internal_auditor` and
  `chief_financial_controller`). No new permission code is invented; `reports.audit.read` is not used.
- `actor` is `null` for system/no-actor rows (`AuditLog.actor_user` is nullable); the other item
  fields (`actor_type`, `action`, `entity_type`, `entity_id`, `created_at`) remain populated.
- `old_value`/`new_value` surface the stored `old_value_json`/`new_value_json` values; `user_agent`
  is intentionally not exposed (not part of §42.1).
- Missing bearer token → `401 AUTH_REQUIRED`; malformed/revoked/expired session → `401 INVALID_TOKEN`;
  authenticated user without the audit-read permission → `403 FORBIDDEN`.

## Workflow event foundation (003B)

`record_workflow_event(...)`

Internal write interface over the canonical `workflows.WorkflowEvent` model and existing physical
`workflow_events` table (`docs/source/data-model.md` §26.2). The physical table was first created by
the 002EX tracer migration; 003B moves final Django model ownership to `sfpcl_credit.workflows`
without dropping or recreating the table. The tracer proof now calls this service and still returns
`workflow_event_id` in transition responses.

Accepted facts:
- `actor` — authenticated `User` or `None`, stored as `triggered_by_user`.
- `workflow_name`, `entity_type`, `entity_id`, `from_state`, `to_state`, `trigger_reason`.
- `action_code` and `metadata` may be passed by callers as explicit boundary facts, but they are not
  persisted because §26.2 defines no action or metadata columns.

`GET /api/v1/workflow-events/`

Read-only, protected endpoint matching `docs/source/api-contracts.md` §42.2. Serialization,
filtering, and pagination live behind `sfpcl_credit/workflows/events.py`;
`sfpcl_credit/workflows/event_views.py` is a thin `require_GET` view. No update/delete endpoint
exists.

Request headers:

```http
Authorization: Bearer <access_token>
X-Request-ID: req-workflow-list
```

Query parameters (all optional):
- `entity_type` — free-text exact match on `WorkflowEvent.entity_type`.
- `entity_id` — UUID; invalid UUID returns `400 VALIDATION_ERROR` with `field_errors.entity_id`.
- `page`, `page_size` — standard top-level pagination (default `page_size` 20, max 100).
- Any other query parameter returns `400 VALIDATION_ERROR` with the unknown key in `field_errors`.

Success (top-level `pagination` envelope, newest-first by `created_at`):

```json
{
  "success": true,
  "data": [
    {
      "workflow_event_id": "uuid",
      "workflow_name": "application",
      "entity_type": "loan_application",
      "entity_id": "uuid",
      "from_state": "draft",
      "to_state": "submitted",
      "triggered_by_user": { "user_id": "uuid", "full_name": "Ivy Auditor" },
      "trigger_reason": "Application submitted for credit review",
      "created_at": "2026-06-22T10:30:00Z"
    }
  ],
  "pagination": { "page": 1, "page_size": 20, "total_count": 1, "total_pages": 1, "has_next": false, "has_previous": false },
  "meta": { "request_id": "req-workflow-list", "timestamp": "...Z", "api_version": "v1" }
}
```

Rules:
- Permission: `audit.workflow_event.read` (002C catalogue). No new workflow-event permission code is invented.
- `triggered_by_user` is `null` for system/no-actor rows.
- Missing bearer token → `401 AUTH_REQUIRED`; malformed/revoked/expired session → `401 INVALID_TOKEN`;
  authenticated user without `audit.workflow_event.read` → `403 FORBIDDEN`.
- Response examples are saved in `.ralph/runs/2026-07-05_083910_normal_run/evidence/api-responses/workflow-events-api-response.txt`.

## Versioned loan-policy configuration (003E)

`GET /api/v1/config/loan-policy/`

Protected read endpoint over `loan_policy_configs` (`docs/source/data-model.md` §25.1 and
`docs/source/api-contracts.md` §41.1). Results use the standard top-level pagination envelope,
ordered newest/effective-first by `effective_from` with `loan_policy_config_id` as a deterministic
secondary key.

Query parameters:
- `page`, `page_size` — standard top-level pagination (default `page_size` 20, max 100).
- Any other query parameter returns `400 VALIDATION_ERROR`.

`POST /api/v1/config/loan-policy/`

Creates a draft config. Request fields mirror the §41.1 request and §25.1 source columns:
`policy_name`, `policy_version`, `effective_from`, nullable `effective_to`,
duration/month/year settings, approval threshold/default scale/share/per-share/interest fields,
re-KYC/retention/grace/extension settings, and nullable `board_approval_reference`. `status`
defaults to `draft`; new configs cannot be created directly as `active` or `retired`.

`PATCH /api/v1/config/loan-policy/{loan_policy_config_id}/`

Updates draft configs only. Patching a non-draft config returns `409 INVALID_STATE_TRANSITION`.
Unknown fields, invalid ISO dates, `effective_to` before `effective_from`, negative decimals,
non-positive required integer settings, or unsupported status values return `400 VALIDATION_ERROR`
with field errors.

`POST /api/v1/config/loan-policy/{loan_policy_config_id}/activate/`

Activates a draft config only when `board_approval_reference` is present, satisfying
`functional-spec.md` M01-FR-015 for the shell. Missing approval evidence returns
`400 VALIDATION_ERROR` with `field_errors.board_approval_reference`. Activation writes:
- one `VersionHistory` row for `versioned_entity_type: "loan_policy_config"`;
- one `AuditLog` row with action `config.loan_policy.activated`;
- a state change to `active`.

Per A-021, if another loan-policy config is already active, activation retires it and sets its
`effective_to` to the day before the newly activated config's `effective_from`.

Mutation audit actions:
- create: `config.loan_policy.created`;
- update: `config.loan_policy.updated`;
- activate: `config.loan_policy.activated`.

Permissions:
- list/read requires `config.loan_policy.read`;
- create/update/activate require `config.loan_policy.manage`;
- missing bearer token returns `401 AUTH_REQUIRED`; authenticated users without the required
  permission return `403 FORBIDDEN` with no config/audit/version write.

`GET /api/v1/version-histories/`

Read-only, protected version-history endpoint matching `docs/source/api-contracts.md` §42.3 over
`version_histories` (`docs/source/data-model.md` §26.3).

Query parameters:
- `versioned_entity_type` — optional exact match.
- `versioned_entity_id` — optional UUID; invalid UUID returns `400 VALIDATION_ERROR`.
- `page`, `page_size` — standard top-level pagination (default `page_size` 20, max 100).
- Any other query parameter returns `400 VALIDATION_ERROR`.

Response items include `version_history_id`, `versioned_entity_type`, `versioned_entity_id`,
`version_number`, `change_summary`, nullable `author`/`reviewer`/`approver` user summaries,
`board_approval_reference`, `effective_from`, nullable `effective_to`, and `created_at`.
Permission: `audit.version_history.read`.

Functional requirement trace:
- M01-FR-001: one or more persisted loan product configurations are supported.
- M01-FR-002: version/effective dates/Board reference are stored on the config; approval authority
  for activation is captured through the `approver` user on `VersionHistory`.
- M01-FR-015: activation is blocked without `board_approval_reference`.
- M01-FR-003 through M01-FR-014 are deferred to later rule/config slices; 003E persists only neutral
  source model fields and does not implement eligibility, share valuation, scale-of-finance,
  approval matrix, interest, charges, document-template, re-KYC, or compliance calculations.

## Document file upload foundation (003C)

`POST /api/v1/document-files/`

Protected multipart upload endpoint matching `docs/source/api-contracts.md` §26.1 and
`docs/source/data-model.md` §16.1. File bytes are stored outside the database through the local
filesystem adapter (`storage_provider: "local"`); the `document_files` table stores metadata,
storage key, uploader, sensitivity, upload timestamp, and SHA-256 checksum. Loan-document/checklist
workflow remains future scope.

Request headers:

```http
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
X-Request-ID: req-document-upload
```

Multipart fields:
- `file` — required file binary.
- `document_category` — required free-text category from the source vocabulary.
- `sensitivity_level` — required; accepted values are `public`, `internal`, `confidential`,
  `restricted`; input is case-normalized to lower case.
- `related_entity_type` — optional free-text entity type, recorded only in the upload audit metadata
  until downstream domain tables exist.
- `related_entity_id` — optional UUID; invalid UUID returns `400 VALIDATION_ERROR` with
  `field_errors.related_entity_id`.

Success data:

```json
{
  "success": true,
  "data": {
    "document_id": "uuid",
    "file_name": "borrower-pan.pdf",
    "mime_type": "application/pdf",
    "file_size_bytes": 245600,
    "sensitivity_level": "restricted",
    "uploaded_at": "2026-06-22T10:30:00Z"
  },
  "meta": { "request_id": "req-document-upload", "timestamp": "...Z", "api_version": "v1" }
}
```

Rules:
- Permission: `documents.file.upload` from the seeded source catalogue.
- Missing bearer token → `401 AUTH_REQUIRED`; malformed/revoked/expired session →
  `401 INVALID_TOKEN`; authenticated user without `documents.file.upload` →
  `403 FORBIDDEN`.
- Missing `file`, `document_category`, or `sensitivity_level` returns `400 VALIDATION_ERROR` with
  field-level errors and no file, metadata, or audit write.
- Invalid `sensitivity_level` or `related_entity_id` returns `400 VALIDATION_ERROR`.
- Successful upload writes exactly one `AuditLog` row with action `documents.file.uploaded`,
  `entity_type: "document_file"`, and `entity_id` equal to the new `document_id`. The audit
  `new_value` includes metadata such as file name, storage provider/key, checksum, sensitivity,
  category, and related entity facts; it never stores raw file bytes.
- Local adapter root defaults to `SFPCL_DOCUMENT_STORAGE_ROOT` or
  `sfpcl_credit/local-document-storage`; tests override this root with a temp directory. Production
  S3/DMS adapters are future work behind the same storage boundary.
- Response examples are saved in `.ralph/runs/2026-07-05_085852_normal_run/evidence/api-responses/document-files-api-response.txt`.

## Document file secure download descriptor (003D)

`GET /api/v1/document-files/{document_id}/download/`

Protected endpoint matching `docs/source/api-contracts.md` §26.2 response option A. It reuses the
003C `document_files` metadata row and storage boundary; it does not stream raw bytes or create new
document metadata tables.

Request headers:

```http
Authorization: Bearer <access_token>
X-Request-ID: req-document-download
```

Success data:

```json
{
  "success": true,
  "data": {
    "download_url": "/api/v1/local-document-files/uuid/download/?expires_at=2026-07-05T04%3A30%3A00Z",
    "expires_at": "2026-07-05T04:30:00Z"
  },
  "meta": { "request_id": "req-document-download", "timestamp": "...Z", "api_version": "v1" }
}
```

Rules:
- Permission: `documents.file.download` from the seeded source catalogue. The upload permission does
  not grant download access.
- The local adapter uses a deterministic, time-limited descriptor for MVP/dev tests because it cannot
  create a true external signed URL. Default expiry is 15 minutes from issuance.
- Missing bearer token → `401 AUTH_REQUIRED`; malformed/revoked/expired session →
  `401 INVALID_TOKEN`; authenticated user without `documents.file.download` →
  `403 FORBIDDEN`.
- Unknown `document_id` returns `404 NOT_FOUND` without file name, storage key, provider details, or
  checksum information.
- The response body contains only `download_url` and `expires_at`; it never exposes `storage_key`,
  checksum, raw bytes, or upload audit metadata.
- Successful descriptor issuance writes exactly one `AuditLog` row with action
  `documents.file.downloaded`, `entity_type: "document_file"`, and `entity_id` equal to the
  downloaded document. Audit `new_value` includes document id, file name, MIME type, file size,
  storage provider, sensitivity level, and expiry timestamp; it deliberately omits storage key,
  checksum, signed secrets, and raw bytes.
- Failed auth, permission, and not-found requests do not write `documents.file.downloaded` audit rows.
- Public, internal, confidential, and restricted documents currently follow the same
  `documents.file.download` permission path until source docs define an implementable sensitivity
  matrix.
- Response examples are saved in `.ralph/runs/2026-07-05_093205_normal_run/evidence/api-responses/document-download-api-response.txt`.
## Communication template shell (003F)

`GET /api/v1/content-templates/`

`POST /api/v1/content-templates/`

`PATCH /api/v1/content-templates/{content_template_id}/`

Metadata-only endpoints matching `docs/source/api-contracts.md` §39.1 and
`docs/source/data-model.md` §24.1. This shell does not render templates with borrower/loan merge
data and does not send communications.

Request headers:

```http
Authorization: Bearer <access_token>
X-Request-ID: req-content-template
```

Create request fields:
- Required: `template_code`, `template_name`, `template_type`, `audience`, `body_template`,
  `approval_status`, `template_version`, `effective_from`.
- Optional: `language_code`, `subject_template`, `variables`, `effective_to`.
- `variables` must be a JSON array of non-empty strings and is persisted to `variables_json`.
- `approval_status` is limited to `draft` or `approved`.
- `effective_from` and `effective_to` use ISO dates; `effective_to` must be on or after
  `effective_from` when supplied.

Success item fields:

```json
{
  "content_template_id": "uuid",
  "template_code": "loan_rejection_email_v1",
  "template_name": "Loan Rejection Email",
  "template_type": "email",
  "language_code": "en",
  "audience": "borrower",
  "subject_template": "Loan Application {{application_reference_number}} - Rejection Note",
  "body_template": "Dear {{borrower_name}}, your application has been rejected.",
  "variables": ["application_reference_number", "borrower_name", "rejection_reason"],
  "approval_status": "approved",
  "template_version": "1.0",
  "effective_from": "2026-04-01",
  "effective_to": null
}
```

Rules:
- List responses use the standard top-level pagination envelope with `page` and `page_size`
  query parameters only; unknown query parameters return `400 VALIDATION_ERROR`.
- Missing bearer token returns `401 AUTH_REQUIRED`; revoked/invalid token returns the existing
  auth `401`; authenticated users without content-template permission return `403 FORBIDDEN`
  before any database write.
- Permission assumption A-022: read requires `communications.content_template.read` or
  `communications.content_template.manage`; writes require `communications.content_template.manage`.
  These narrow codes are used instead of `config.loan_policy.*`, `documents.template.*`, or
  communication-send permissions.
- Duplicate `template_code` returns `400 VALIDATION_ERROR` with `field_errors.template_code` and no
  audit row.
- Unknown `content_template_id` returns `404 NOT_FOUND`.
- Create/update write `AuditLog` actions `communications.content_template.created` and
  `communications.content_template.updated`. Audit metadata includes template id/code/name/type,
  audience, approval status, version, variables, and effective dates, but no rendered borrower or
  loan-specific merge output.

## Asynchronous communication dispatch (003I, 009H7-009H9C)

`POST /api/v1/communications/send/`

`GET /api/v1/communications/?related_entity_type=loan_application&related_entity_id=uuid`

Protected endpoints matching `docs/source/api-contracts.md` §39.2-§39.3 and
`docs/source/data-model.md` §24.2. The send endpoint validates and renders an approved/effective
template, persists one pending Communication plus one durable delivery job, and publishes the job
only after transaction commit. HTTP never calls a provider. The registered worker routes Email to
the configured `EmailAdapter` and SMS to the separately configured `SmsAdapter`; manual/default
adapters retain retryable pending/failed truth and never fabricate provider acceptance.

Send request fields:
- Required: `related_entity_type`, `related_entity_id`, `recipient_party_type`, `channel`,
  `content_template_id`, `merge_data`.
- Optional: `recipient_party_id`, `recipient_address`.
- `related_entity_id`, `recipient_party_id`, and `content_template_id` must be UUIDs when supplied.
- Email requires an Email template and valid email recipient. SMS requires an SMS template and an
  E.164 mobile recipient. Phone/courier return stable `400 VALIDATION_ERROR` because this endpoint
  has no source-owned manual-task implementation; neither can cross an Email/SMS provider seam.
- SMS rejects PAN, Aadhaar, full bank-account/cheque/IFSC/ciphertext variable names and rendered
  values before any Communication, job, notification, or audit write.
- `content_template_id` must reference an `approved` template whose `effective_from`/`effective_to`
  window includes the server's current local date.
- Per A-025, `merge_data` must exactly match `ContentTemplate.variables_json`; missing or extra keys
  return `400 VALIDATION_ERROR` before any communication or audit write.

Success data:

```json
{
  "communication_id": "uuid",
  "related_entity_type": "loan_application",
  "related_entity_id": "uuid",
  "recipient_party_type": "borrower",
  "recipient_party_id": "uuid",
  "recipient_address": "borrower@sfpcl.example",
  "channel": "email",
  "content_template_id": "uuid",
  "subject_snapshot": "Sanction LA-2026-0001",
  "body_snapshot": "Dear Ananya Rao, your loan LA-2026-0001 is sanctioned.",
  "sent_by_user_id": "uuid",
  "sent_at": null,
  "delivery_status": "pending",
  "acknowledgement_status": null,
  "external_message_id": null
}
```

An exact repeated actor/object/channel/payload/key returns the source §45.2 shape and the retained
first response; it performs no provider call or write:

```json
{
  "idempotency_replayed": true,
  "original_response": {}
}
```

Changed, cross-actor, cross-object, or cross-channel reuse returns zero-write `409 CONFLICT`.
Accepted Email/SMS delivery freezes one immutable communications-owned provider-evidence row bound
to the job, communication, channel, payload digest, key, actor, adapter identity, provider result,
and acceptance time before the mutable delivery projections become `sent`. Worker crash/replay
reconciles that evidence and does not re-enter the provider.

List query parameters:
- Required: `related_entity_type`, `related_entity_id`.
- Optional: `page`, `page_size` using standard top-level pagination.
- Unknown query parameters or invalid UUIDs return `400 VALIDATION_ERROR`.

Rules:
- Missing bearer token returns `401 AUTH_REQUIRED`; revoked/invalid token returns the existing auth
  `401`; authenticated users without the relevant communication permission return
  `403 FORBIDDEN` before any write.
- Permission assumption A-025: list/read requires `communications.communication.read` or
  `communications.communication.send`; send requires `communications.communication.send`. These
  narrow codes are used instead of broad report, document-template, or config permissions.
- Successful send writes exactly one `AuditLog` row with action
  `communications.communication.created`, `entity_type: "communication"`, and `entity_id` equal to
  the new communication id. Audit metadata includes related entity, recipient party, address,
  channel, template id, sender id, and delivery status. It deliberately omits `subject_snapshot`,
  `body_snapshot`, `merge_data`, provider credentials, and external secrets.
- M16-FR-001, M16-FR-002, M16-FR-004, M16-FR-005, and M16-FR-007 are implemented for generic
  Email/SMS queueing, adapter dispatch, retained status/evidence, templates, and related records.
  Hard-copy task generation and manual phone-call reminders remain owned by later source-specific
  workflows. Current-user notification-center read/unread/action state is implemented separately by
  003IA under `GET /api/v1/notifications/`.
- Response examples are saved in
  `.ralph/runs/2026-07-06_105004_normal_run/evidence/api-examples/communications-api-examples.json`.

## Notification inbox APIs (003IA)

`GET /api/v1/notifications/`

Protected current-user inbox endpoint for S04. It is intentionally separate from
`GET /api/v1/communications/`, which remains related-entity communication history.

Query parameters:
- Optional: `page`, `page_size` using standard top-level pagination.
- Optional: `read_status` (`all`, `read`, `unread`; default `all`).
- Optional: `severity` (`info`, `warning`, `urgent`).
- Optional: `category`.
- Unknown query parameters return `400 VALIDATION_ERROR`.

Success data items include:
- `notification_id`, optional `communication_id`, `notification_type`, `category`, `severity`,
  `title`, `message`;
- optional linked record fields `related_entity_type`, `related_entity_id`, `action_label`,
  `action_url`;
- `sender`, `recipient`, `read`, `read_at`, `read_by_user_id`, `read_state_version`, and
  `created_at`.

Response examples are saved in
`.ralph/runs/2026-07-06_164949_normal_run/evidence/api-responses/notifications-api-example.json`.

`POST /api/v1/notifications/{notification_id}/mark-read/`

Request:

```json
{ "read_state_version": 1 }
```

Rules:
- Missing bearer token returns `401 AUTH_REQUIRED`; revoked/invalid token returns the existing auth
  `401`; authenticated users without `communications.notification.read` return
  `403 FORBIDDEN`.
- List and mark-read are scoped to notifications addressed directly to the current user, to the
  current user's active primary role code, or to one of the current user's active team codes.
  Other users' notifications are excluded from list results and return `404 NOT_FOUND` on mark-read.
- `read_state_version` is required on mark-read. If the submitted version does not match the
  persisted notification version, the endpoint returns `409 STALE_WRITE`.
- Successful mark-read persists `read_at`, `read_by_user_id`, increments `read_state_version`, and
  writes one `AuditLog` row with action `communications.notification.marked_read`.
- 003IA also creates a notification row when `POST /api/v1/communications/send/` addresses a staff
  recipient using `recipient_party_type` of `user`, `staff_user`, or `internal_user` and a
  `recipient_party_id` matching a backend user. Borrower/member communications and provider
  delivery remain outside this inbox.
- Permission assumption A-026: `communications.notification.read` is the narrow S04 permission and
  is seeded to active internal roles with existing source-backed permission sets. The deliberately
  permission-neutral `it_head` and `sales_team_user` demo/source roles remain ungranted pending
  source confirmation.

## Dashboard task summary shell (003G)

`GET /api/v1/dashboard/`

Protected endpoint matching `docs/source/api-contracts.md` §43.1 for the role-based dashboard
summary. Specialist dashboard endpoints from §43.2-§43.4 are deferred; this slice exposes only the
single role-context shell.

Request headers:

```http
Authorization: Bearer <access_token>
X-Request-ID: req-dashboard
```

Success data:

```json
{
  "role_context": "credit_manager",
  "cards": [
    {
      "code": "applications_pending_completeness",
      "label": "Applications pending completeness",
      "count": 0,
      "link": "/applications?status=pending_completeness"
    }
  ],
  "tasks": []
}
```

Rules:
- No query parameters are supported. Any query parameter returns `400 VALIDATION_ERROR` with the
  unknown parameter in `field_errors`.
- Missing bearer token returns `401 AUTH_REQUIRED`; revoked/invalid token returns `401`; an
  authenticated user without the dashboard scope returns `403 FORBIDDEN`.
- Permission assumption A-023: dashboard read requires `management_readonly`, the source §19.1
  dashboard/summary scope. This is used instead of broad report/export permissions or an invented
  `dashboard.read` code.
- Role contexts currently returned from primary role:
  `credit_manager`, `sanction_committee`, `compliance`, `treasury`, or `management`.
- Cards use source-named shell codes from the §43.1 example and functional-spec §12.2-§12.6
  dashboard widget lists. All `count` values are `0` because application, appraisal, sanction,
  compliance, treasury, DPD, reminder, default, and management-report tables/calculations are not
  implemented yet.
- `tasks` is an empty list because no source-backed task persistence table exists yet.
- The response returns only summary metadata fields: `role_context`, `cards[].code`,
  `cards[].label`, `cards[].count`, `cards[].link`, and `tasks[]`. It does not return borrower,
  member, loan-account, document, or other sensitive entity values.
- Read-only dashboard access does not write `AuditLog` rows in this shell.
- Response examples are saved in
  `.ralph/runs/2026-07-05_200043_normal_run/evidence/api-responses/dashboard-api-response.txt`.
- Frontend wiring implemented in 003H (`2026-07-06_102639_normal_run`): the staff Dashboard page
  now calls this endpoint with the stored bearer session, renders `cards[]` through the existing
  KPI-card pattern, renders `tasks[]` through the existing task-queue pattern, and uses existing
  alert/empty patterns for loading, empty, `401`, `403`, and server/network errors. Frontend link
  translation follows A-024; unknown future links are left inactive instead of creating new routes
  in this dashboard slice.

## Member portal dashboard/profile/supply APIs (005FB)

Protected borrower portal endpoints:
- `GET /api/v1/portal/dashboard/`
- `GET /api/v1/portal/profile/`
- `GET /api/v1/portal/produce-supply/`

Rules:
- The member scope comes only from the authenticated active `PortalAccount` linked to the bearer
  token user. A client-supplied `member_id` query value that differs from that account returns
  `403 OBJECT_ACCESS_DENIED`; it is never ignored, disclosed, or used for a read/write.
- If the linked `PortalAccount` becomes suspended/inactive after token issuance, the shared
  session-bound auth validator revokes the active session with reason
  `portal_account_status_changed` and these endpoints return `401 INVALID_TOKEN`.
- Staff or non-portal tokens return `403 FORBIDDEN`; missing/invalid bearer tokens return
  the standard auth errors.
- Dashboard returns own member snapshot, own application counts from implemented
  `loan_applications`, active loan placeholder counts of zero until loan accounts exist, open
  deficiency pending-action count from `deficiencies`, and zero placeholders for future signature,
  repayment, KYC-update, and closure actions.
- Profile returns the existing masked member profile plus own nominees, shareholdings, land
  holdings, crop plans, KYC profile, bank accounts, and cancelled cheques. Portal profile responses
  force PAN/Aadhaar `can_view_full = false` and expose no full bank account values.
- Produce supply returns portal-account-scoped persisted records with no member identifier or
  staff actions. Every record includes the member module's `qualifying` boolean and stable nullable
  `non_qualifying_reason`; summary includes the immutable `result_id` and
  `calculated_as_of_date`. `source_status` is `persisted_qualifying_verified_records` when source-eligible
  verified history exists and `persisted_no_qualifying_verified_records` otherwise. Summary totals
  and continuity derive only from canonical-year, eligible-entity/route, evidence-referenced,
  verified rows; pending and malformed legacy rows remain visible but do not contribute.
  because `data-model.md` defines `produce_supply_records` but no backend model exists yet.

Frontend wiring:
- MP03, MP04, and prototype `MP22_ProduceSupply.tsx` call these endpoints through
  `sfpcl-lms/src/services/portalApi.ts` with the stored portal bearer session.

### Staff produce-supply capture and verification (006Z/006Z3)

- `POST /api/v1/members/{member_id}/produce-supply-records/` requires
  `members.active_status.calculate` and an object body containing the current integer member
  `version`, canonical `financial_year` (`YYYY-YY`), eligible `supplied_to_entity_type`, consistent
  `supply_route`, and non-blank `evidence_reference`. Unknown fields, invalid UUID relationships,
  and negative/over-precision quantity or value facts return `400 VALIDATION_ERROR`; stale member
  versions return `409 STALE_WRITE` without record, history, or audit evidence.
  An existing member outside the actor's action-specific persisted scope returns
  `403 OBJECT_ACCESS_DENIED` without supply, member-version, history, or audit writes.
- Direct supply forbids `producer_institution_member_id`; the Producer Institution route requires
  an active, non-self FPC/Producer Institution member UUID. Subsidiary and step-down subsidiary
  destinations require `supplied_to_entity_id`.
- `POST /api/v1/produce-supply-records/{record_id}/verify/` retains maker-checker separation and
  the current supply-record `version`; stale verification returns `409 STALE_WRITE`. Object-scope
  denial is `403 OBJECT_ACCESS_DENIED`, while maker-checker denial remains `403 FORBIDDEN`.
- `POST /api/v1/members/{member_id}/active-status/verify/` requires
  `members.active_status.verify` plus `result_id`, current member `version`, ISO `as_of_date`,
  `decision` (`active`, `inactive`, or `relaxation`), and a non-blank `reason`; missing/future dates
  and unknown fields return `400 VALIDATION_ERROR`. The permission authorizes only the named action;
  object access additionally requires the same persisted, action-specific member-scope assignment
  used by member list/detail (`global`, actor-team/member, actor/member assignment, or created-by).
  Role provenance, action permission alone, caller flags, and unowned records never create scope.
  A missing or existing out-of-scope member returns the same `403 OBJECT_ACCESS_DENIED`. The
  calculated route and decision must
  agree exactly (`pass`/`active`, `relaxation`/`relaxation`, otherwise `inactive`); mismatches return
  `409 INVALID_DECISION`. It rejects actors who captured or verified any qualifying supply/service/
  relaxation evidence, stale/changed results, stale versions, unsupported decisions,
  and repeated decisions without audit/history evidence. A winner returns the exact complete dated
  result snapshot and atomically creates an effective-dated `active_member_statuses` record, closes
  the prior current record, points the Member projection at the new record primary key, and records
  the same projection in member history and audit. Internal snapshots retain row/evidence/verifier
  facts; borrower portal supply rows deliberately omit those internal fields.

### Staff member list/detail scope and nondisclosure (006Z11)

- `GET /api/v1/members/` first requires `members.member.read`, then applies the authenticated
  actor's persisted action-specific member scope before search, filtering, count, and pagination.
  `pagination.total_count`, pages, and rows therefore contain no fact about excluded members.
- `GET /api/v1/members/{member_id}/` applies the identical predicate. An existing excluded member
  returns `403 OBJECT_ACCESS_DENIED`; an in-scope unknown identifier returns `404 NOT_FOUND`.
- Scope and action are independent. A global assignment for read does not authorize verify,
  identity approval, update, calculation, or evidence maintenance; each write requires its own
  action permission and assignment/creator fact. No default global assignment is seeded.
- Service/relaxation evidence retains every creator and material updater as immutable maker
  provenance. Any maker is denied verification of a derived active-member result with zero status,
  history, audit, or workflow writes, even after another actor updates the evidence.

## Member portal application APIs (005G)

Protected borrower portal endpoints:
- `GET /api/v1/portal/applications/`
- `POST /api/v1/portal/applications/`
- `GET /api/v1/portal/applications/{loan_application_id}/`
- `PATCH /api/v1/portal/applications/{loan_application_id}/`
- `POST /api/v1/portal/applications/{loan_application_id}/submit/`

Rules:
- Scope comes only from the authenticated active `PortalAccount.member_id`. Query/path/payload
  member IDs cannot broaden access.
- If the linked `PortalAccount` becomes suspended/inactive after token issuance, the shared
  session-bound auth validator revokes the active session with reason
  `portal_account_status_changed`; old-token portal application calls return
  `401 INVALID_TOKEN` before creating applications, audit rows, workflow events, register rows,
  references, or visible sequence side effects.
- Staff or non-portal tokens return `403 FORBIDDEN`; cross-member create/read/update/submit
  returns `403 OBJECT_ACCESS_DENIED` and creates no application, audit row, workflow event, register
  row, reference, or visible sequence side effect.
- Create/update/submit reuse the existing 005A/005B application service behavior and workflow
  events with the linked portal user as actor. Borrower portal routes write metadata-only source
  portal audit actions: `portal.application.draft_created`, `portal.application.saved`, and
  `portal.application.submitted`. Staff application routes keep internal
  `applications.loan_application.created`, `applications.loan_application.updated`, and
  `applications.loan_application.submitted` audit actions.
- Draft save can be incomplete. Create/update accept `nominee_id` through the shared application
  nominee-validation module interface. Unknown, cross-member, minor, and missing-age-evidence
  create/PATCH attempts return `400 VALIDATION_ERROR` with `field_errors.nominee_id` and preserve
  the previously serialized application, status, selection, audit counts, and workflow counts.
  Submit requires own member, positive requested amount, declared purpose, purpose
  category, and one stored adult own-member nominee.
- Submitted applications remain without an `LO...` reference until staff completeness pass
  generates it.
- Returned-incomplete applications serialize borrower-facing rectification state:
  `application_status = incomplete_returned`, `completeness_status = incomplete`,
  `current_stage = initial_loan_request`, `pending_with = Borrower`, open deficiency count, and
  open deficiency item metadata.
- Detail responses expose the same metadata-only `nominee` summary as staff detail. MP10 renders
  nominee ID, name, age snapshot, minor/adult status, KYC status, relationship, and signature-required
  status. Responses expose portal-safe application summary/detail fields only: application IDs/reference
  display, dates, requested amount, purpose, status/stage/completeness, pending owner, borrower
  action, open deficiency count, member snapshot, timeline, and open deficiency metadata.
- Responses do not expose staff completeness/reference-generation/return/resolve actions, PAN,
  Aadhaar, full bank-account values, encrypted values, token hashes, raw document contents, or
  staff-only document internals.

Example detail response:

```json
{
  "success": true,
  "data": {
    "loan_application_id": "uuid",
    "application_reference_number": null,
    "display_reference": "A1B2C3D4",
    "application_status": "submitted",
    "current_stage": "initial_loan_request",
    "completeness_status": "not_started",
    "pending_with": "SFPCL",
    "borrower_action": "No action required",
    "open_deficiency_count": 0
  }
}
```

Frontend wiring:
- MP05 saves/submits through these endpoints.
- MP09 renders list, loading, empty, error, and returned-incomplete states from
  `GET /api/v1/portal/applications/`.
- MP10 renders selected application status/detail from
  `GET /api/v1/portal/applications/{loan_application_id}/`.

### Portal application limit projection (006Z2)

- `GET /api/v1/portal/application-limit-projection/?requested_amount={money}` derives member scope
  only from the active `PortalAccount` and is read-only. A different client-supplied `member_id`
  returns `403 OBJECT_ACCESS_DENIED` without assessment, audit, or workflow writes.
- `status = available` returns the server-calculated shareholding, land, and effective lower limit,
  the effective policy version/date, and the server-owned requested-amount advisory flags.
- Missing, stale, future, closed, manual, or provenance-mismatched active-member authority—and
  incomplete or contradictory verified share/land facts—returns `status = unavailable` with null
  amounts and no guessed zero.
- The response deliberately omits member/effective-record/result IDs, evidence rows/references,
  verifier and decision facts, configuration IDs, and staff actions.

## Eligibility assessment APIs (006A-006B)

Protected staff endpoints:
- `POST /api/v1/loan-applications/{loan_application_id}/eligibility-assessment/run/`
- `GET /api/v1/loan-applications/{loan_application_id}/eligibility-assessment/`

Rules:
- Run requires `credit.eligibility.run` and the existing loan-application object-access boundary.
  A user missing the global run permission receives `403 FORBIDDEN`; a user with the
  permission but outside the application scope receives `403 OBJECT_ACCESS_DENIED`.
  After application authority succeeds, a query/body `member_id` different from the application's
  stored member also returns `403 OBJECT_ACCESS_DENIED` without assessment, audit, or workflow
  writes; the actorless member calculation always derives its member from the application.
- Read requires the existing `applications.loan_application.read` permission and object-access
  boundary used by application detail.
- Missing applications return `404 NOT_FOUND`. Reading before an assessment exists returns
  `404 NOT_FOUND`.
- Run is allowed only after formal reference generation: `application_reference_number` starts
  with `LO`, `application_status = reference_generated`, `completeness_status = complete`, and
  `current_stage = credit_assessment`. Other states return `409 INVALID_STATE_TRANSITION`.
- `member_active_check` is calculated through `members.modules.active_member_status`:
  - `pass` when an active individual/FPC/Producer Institution has recorded service usage and four
    uninterrupted, completed financial years of qualifying verified produce-supply evidence.
  - `relaxation` for an individual with three recorded continuous employment/service years, or for
    a recorded relaxation backed by at least one completed qualifying supply year.
  - `fail` when the member's `membership_status` is not `active`.
  - `manual_evidence_required` when BR-004 through BR-007 require produce/service history but the
    current persistence has no source-backed history rows to calculate it.
- Responses persist and expose `active_member_snapshot`, including `result_id`,
  `calculated_as_of_date`, member/rule route facts, continuity, and every classified supply row.
  Later member/supply changes never rewrite an application's stored eligibility snapshot.
- 006B computes these additional source-backed checks:
  - `default_check = no_default` only when `Member.default_status = no_default`; other existing
    default-like values return `default_found`.
  - `document_check = complete` only when the 005D/005E required checklist metadata has no
    blocking submitted/verified item; otherwise it returns `incomplete`.
  - `terms_acceptance_check = accepted` only when `LoanApplication.terms_acceptance_flag = true`;
    otherwise it returns `pending`.
  - `purpose_check = agriculture_aligned` only when `purpose_category` is `crop_production` or
    `agriculture_activity`; otherwise it returns `non_agriculture`.
  - `nominee_check` reads only `LoanApplication.nominee`: `valid` for the stored adult nominee,
    `minor` for a legacy invalid stored nominee, and `pending` for a legacy null or missing-age
    selection. Reverse-linked member nominee rows never influence the result.
- `overall_result = eligible` only when every implemented check passes. It is `ineligible` when
  membership/default/document/terms/purpose/minor-nominee blockers fail, and
  `pending_manual_evidence` when active-member or application-specific nominee evidence remains
  unresolved.
- Ineligible assessment results do not advance `application_status` or `current_stage`.
- Successful run writes metadata-only `eligibility.assessed` audit and an
  `eligibility_assessment` workflow event. Denied and invalid-state paths create no assessment,
  audit row, or workflow event.

Response data fields:

```json
{
  "eligibility_assessment_id": "uuid",
  "loan_application_id": "uuid",
  "member_active_check": "pass",
  "default_check": "no_default",
  "document_check": "complete",
  "terms_acceptance_check": "accepted",
  "purpose_check": "agriculture_aligned",
  "nominee_check": "valid",
  "overall_result": "eligible",
  "assessment_notes": "All mandatory eligibility criteria passed.",
  "assessed_by_user_id": "uuid",
  "assessed_at": "2026-07-10T00:00:00Z"
}
```

## Loan-limit calculation and stored snapshot APIs (006C-006D)

Protected staff endpoints:
- `POST /api/v1/loan-applications/{loan_application_id}/loan-limit-assessment/calculate/`
- `GET /api/v1/loan-applications/{loan_application_id}/loan-limit-assessment/`

Request fields:
- `shareholding_id`, non-empty `land_holding_ids`, `crop_plan_id`, positive `requested_amount`,
  and ISO `calculation_date` are required; unknown fields return `400 VALIDATION_ERROR`.

Rules:
- Requires `credit.loan_limit.calculate` plus the existing application object-access boundary.
- Requires the stored 006B assessment to have `overall_result = eligible`; absent,
  `pending_manual_evidence`, and `ineligible` assessments return `409 INVALID_STATE_TRANSITION`.
- Shareholding, every land holding, and crop plan must belong to the application member. Every
  selected land holding must be `verified`. The selected crop plan must be `verified`, linked to
  this loan application, and agriculture aligned. Null crop-plan links, links to another
  application, and non-agriculture-aligned crop plans are rejected. The request amount must match
  the persisted application request amount.
- Cultivated acreage is accepted only when the normalized Decimal values agree across the total
  selected verified land acreage, the application-linked verified crop plan's planned acreage, and
  the member profile's `land_area_under_cultivation_acres` when that profile value exists. Decimal
  formatting differences such as `5`, `5.0`, and `5.00` are equal. A disagreement returns
  `400 VALIDATION_ERROR` with `error.field_errors.cultivated_acreage =
  "CULTIVATED_ACREAGE_UNRESOLVED"` and creates no assessment, audit, or workflow evidence.
- Exactly one active loan policy must cover `calculation_date`; it must include Board approval
  metadata, a positive scale of finance, and a positive percentage and/or per-share cap. Missing,
  overlapping, or unresolved policy configuration returns `400 VALIDATION_ERROR` and creates no
  calculation evidence.
- Percentage rule: `valuation_per_share × percentage / 100`; when a per-share cap is configured,
  it is the ceiling. Share limit is shares multiplied by the resulting per-share amount.
- Land limit uses the agreed cultivated acreage multiplied by configured scale of finance. Final
  eligible amount is the lower of share and land limits.
- Requested amount equal to or below the final limit needs no exception. An amount above it sets
  both boundary flags and returns `REQUESTED_AMOUNT_EXCEEDS_LIMIT`.
- A successful rerun updates the one-to-one assessment while preserving its UUID. Each successful
  calculation atomically writes `loan_limit.calculated` audit metadata and a
  `loan_limit_assessment` workflow event; denied/invalid/validation paths write none.
- GET requires `applications.loan_application.read` and the existing application object-access
  boundary. It returns `404 NOT_FOUND` when the application or stored assessment does not exist.
- GET performs no calculation and writes no audit/workflow evidence. Every response field below,
  including warning output and `configuration_source`, is serialized from the assessment row.
- Number/share valuation, percentage/cap, land area/scale, all computed amounts, requested amount,
  boundary flags, member/shareholding identifiers, rule version, actor/time, and policy config
  UUID/name/Board reference are immutable snapshot facts until a new successful calculate call
  replaces them. Changes to application, member source records, land/crop/shareholding rows, or
  loan-policy config do not alter an existing GET response.
- Failed reruns leave the prior assessment and evidence counts unchanged. Successful rerun audit
  metadata contains the complete prior and replacement assessment snapshots.

Response data fields:

```json
{
  "loan_limit_assessment_id": "uuid",
  "loan_application_id": "uuid",
  "member_id": "uuid",
  "shareholding_id": "uuid",
  "number_of_shares": 100,
  "valuation_per_share": "2000.00",
  "share_limit_percentage": "10.0000",
  "per_share_cap_amount": "200.00",
  "shareholding_based_limit_amount": "20000.00",
  "land_area_acres": "5.00",
  "scale_of_finance_per_acre_amount": "20000.00",
  "land_based_limit_amount": "100000.00",
  "final_eligible_loan_amount": "20000.00",
  "requested_amount": "400000.00",
  "amount_within_limit_flag": false,
  "exception_required_flag": true,
  "calculation_rule_version": "loan-policy-v1.0",
  "configuration_source": {
    "type": "loan_policy_config",
    "loan_policy_config_id": "uuid",
    "policy_name": "Board-approved member loan policy",
    "board_approval_reference": "BOARD/2026/006C"
  },
  "calculated_by_user_id": "uuid",
  "calculated_at": "2026-07-10T00:00:00Z",
  "warnings": [
    {
      "code": "REQUESTED_AMOUNT_EXCEEDS_LIMIT",
      "message": "Requested amount exceeds final eligible loan amount."
    }
  ]
}
```

## Appraisal-note preparation and Credit Manager review APIs (006E/006E2/006F/006F2/006E3/006E4)

Protected staff endpoints:
- `POST /api/v1/loan-applications/{loan_application_id}/appraisal-note/`
- `GET /api/v1/loan-applications/{loan_application_id}/appraisal-note/`
- `PATCH /api/v1/loan-applications/{loan_application_id}/appraisal-note/`
- `POST /api/v1/appraisal-notes/{loan_appraisal_note_id}/submit-for-review/`
- `POST /api/v1/appraisal-notes/{loan_appraisal_note_id}/revalidate-prerequisites/`
- `POST /api/v1/appraisal-notes/{loan_appraisal_note_id}/review/`

Rules:
- Create requires `credit.appraisal.create`, `credit.risk_assessment.manage`, and the existing
  application object-access boundary. It requires a stored eligibility projection with
  `overall_result = eligible` and a stored loan-limit projection; missing or non-eligible facts
  return `409 INVALID_STATE_TRANSITION` without appraisal, risk, audit, or workflow rows.
- One appraisal and one linked risk assessment are stored per loan application. Create copies the
  exact canonical redacted projections returned by `EligibilityAssessmentModule` and
  `LoanLimitCalculator`, plus their UUID provenance. GET, PATCH amount/exception validation,
  submit, review, and sanction consumers use those appraisal-owned frozen projections; a later
  successful same-UUID assessment rerun cannot reinterpret the appraisal.
- Required summaries and `repayment_capacity_notes` are non-blank. Recommended amount is positive; optional tenure is a positive
  integer; supplied interest type is `floating`; recommendation is `approve`, `reject`, or
  `conditions`; all four risk ratings are `low`, `medium`, or `high`. Unknown top-level or nested
  fields return `400 VALIDATION_ERROR`.
- A recommendation above the frozen final eligible amount is rejected unless that frozen
  loan-limit projection already has `exception_required_flag = true`; this contract does not create an
  exception approval.
- PATCH is draft-only and changes supplied fields only. It requires `credit.appraisal.update`;
  changing nested risk fields additionally requires `credit.risk_assessment.manage`.
- GET is side-effect free and is allowed to scoped holders of create/update/submit-review or the
  Credit Manager review permission. Missing notes return `404 NOT_FOUND`.
- `tat_due_at` is application `created_at + 2 days` and never resets. At the exact due instant TAT
  is `within_tat`; later preparation/submission is `breached`.
- Submit requires `credit.appraisal.submit_review`, object scope, and non-blank `remarks`; it
  persists trimmed remarks on the appraisal and atomically transitions `draft -> review_pending`
  once. Submit additionally requires `prerequisite_provenance = verified`; repeated submit and
  later PATCH return `409 INVALID_STATE_TRANSITION`.
- The revalidation action accepts only `{}`, requires `credit.appraisal.update` plus
  `credit.risk_assessment.manage` and object scope, and replaces prerequisite IDs/projections/
  provenance with the current public eligible projections. Malformed JSON and unknown fields
  return `400 VALIDATION_ERROR` without writes. A legacy `draft` stays draft; a legacy
  `review_pending` stays pending for an independent Credit Manager decision. A legacy `reviewed`
  row returns to `draft` and clears only its mutable latest-review projection (decision, comments,
  reviewer, and decision time), while immutable `review_history[]` remains unchanged. It then
  requires maker resubmission and a fresh review before sanction. Legacy `rejected` and
  `submitted_to_sanction_committee` rows return `409 INVALID_STATE_TRANSITION` and remain visibly
  quarantined for governed manual repair. Revalidation never changes recommendation, repayment,
  risk, summary, TAT, preparer, or prior-history facts.
- Create/update/submit write `appraisal.created`, `appraisal.updated`, or
  `appraisal.submitted_for_review` metadata-only audit/workflow evidence. Free-text summaries,
  mitigation notes, repayment-capacity notes, and submit remarks are never copied into evidence
  JSON. Submit audit metadata records only `submission_reason_exists` and its appraisal owner ID;
  revalidation metadata records projection UUIDs, provenance, prior/new appraisal state, and a
  boolean review-authority-invalidated flag only; it does not copy review comments, appraisal
  summaries, financial values, or risk text.
- Review always requires `decision` and non-blank `review_comments`; `decision` is `reviewed`,
  `returned`, or `rejected`. `reviewed` and `returned` continue to accept exactly those two fields.
  `rejected` additionally requires the existing 005H rejection-note fields
  `rejection_reason_category`, non-blank `detailed_reason`, boolean `reapply_allowed_flag`, and
  `communication_mode`; the workflow fixes `rejection_stage = credit_assessment`. Missing, invalid,
  blank, or unknown fields return `400 VALIDATION_ERROR` without success evidence.
- Every review decision requires `credit.appraisal.review`, active primary-role membership as
  `credit_manager`, Credit Manager credit-domain object access, `review_pending` state,
  `prerequisite_provenance = verified`, and a reviewer other than the preparer. Permission granted
  to another role and owner/receiver scope do not confer review authority. Missing role/permission
  returns `403 FORBIDDEN`; an actual Credit Manager outside the domain returns the distinct
  `403 OBJECT_ACCESS_DENIED`.
- `reviewed` transitions to terminal appraisal state `reviewed`. `returned` records the same
  reviewer/time/comment/decision facts and transitions to `draft`, where the maker must revise and
  resubmit before another review. Draft, reviewed, repeated, and other non-pending review attempts
  return `409 INVALID_STATE_TRANSITION`.
- `rejected` atomically transitions to terminal appraisal state `rejected` and creates exactly one
  linked existing 005H rejection-note draft. Its response nests the serialized `rejection_note`,
  including `note_status = draft`, derived `communication_status = not_sent`, null send facts, and
  the appraisal/application/note IDs. It does not send communication or create a sanction/approval
  case. Repeated rejection returns `409` and cannot create a duplicate note.
- Every successful `reviewed`, `returned`, or `rejected` action appends one immutable
  `review_history[]` item with `appraisal_review_decision_id`, decision, non-blank comments,
  reviewer summary, decision time, from/to states, and `history_provenance`. New decisions use
  `native`; migration backfill uses `legacy_latest_only` and represents only the latest known
  legacy decision. The appraisal's top-level decision/comments/reviewer/time remain the latest
  projection and may be replaced by a later review cycle without changing history.
- Review never reads current eligibility or loan-limit rows. It preserves the appraisal-owned
  projections, recommendation/terms, repayment-capacity and submission reasons, linked risk, and
  TAT facts. Successful decisions atomically write `appraisal.reviewed` or `appraisal.returned`
  audit/workflow evidence containing the immutable decision ID plus appraisal/application IDs,
  state, decision, actor/time, and request ID; free-text review comments and appraisal/risk
  projections are excluded.
- Rejected review uses the same outer transaction for appraisal state, rejection-note persistence,
  both metadata evidence streams, and both workflow events. Any note/audit/workflow failure rolls
  back all writes. `appraisal.rejected` evidence may contain the note ID, category, state, actor,
  time, and request ID, but excludes `review_comments` and `detailed_reason`.

Rejected review request:

```json
{
  "decision": "rejected",
  "review_comments": "Independent credit review completed.",
  "rejection_reason_category": "eligibility",
  "detailed_reason": "Verified appraisal facts do not meet credit criteria.",
  "reapply_allowed_flag": true,
  "communication_mode": "email"
}
```

Response data includes appraisal/application/prerequisite IDs, exact `eligibility_snapshot` and
`loan_limit_snapshot`, `prerequisite_provenance = verified|legacy_unverified`, prepared-user
summary/time, immutable TAT due/status, `repayment_capacity_notes`, all stored recommendation-term
facts, linked risk assessment, recommendation, latest review decision/comments/reviewer/time,
ordered immutable `review_history[]`, and
`appraisal_status = draft|review_pending|reviewed|rejected`. A successful rejected-review response
also includes the nested existing rejection-note representation and links its UUID to the appraisal
audit metadata.

## Submit appraisal to Sanction Committee API (006G/006G2/006G3)

Protected Credit Manager endpoint:

- `POST /api/v1/loan-applications/{loan_application_id}/submit-to-sanction-committee/`
- `GET /api/v1/loan-applications/{loan_application_id}/sanction-case/`

The submit response and every later case read return the exact workflow-event UUID durably linked
to that approval case. The read path never substitutes a newer application workflow event.

POST request is exactly `{ "remarks": "non-blank reason" }`. Malformed JSON, a non-object body,
missing/blank remarks, or any unknown field returns `400 VALIDATION_ERROR`. The action requires active `credit_manager` role authority,
`credit.appraisal.submit_sanction`, and the existing Credit Manager credit-domain object boundary;
permission/role failures return `403 FORBIDDEN` and out-of-domain applications return
`403 OBJECT_ACCESS_DENIED`.

Submission requires one `reviewed` appraisal with verified frozen prerequisite projections, a
complete linked risk assessment, populated latest review facts, and at least one immutable review
row. The latest ordered row must be `native|legacy_latest_only` and exactly match the appraisal's
`reviewed` decision, reviewer, time, comments, and `to_state`. Missing, draft, review-pending,
returned, rejected, inconsistent, or repeated paths return `409 INVALID_STATE_TRANSITION` without
case, state, audit, workflow, history, or rejection-note side effects.

The mutation locks application, appraisal, immutable review history, then the case namespace. It
atomically creates one unique pending sanction case, copies only the frozen loan-limit exception
flag, and changes both application and appraisal status to
`submitted_to_sanction_committee`. It does not evaluate the approval matrix, assign approvers,
create an exception decision, or perform a committee action.

Response data:

```json
{
  "approval_case_id": "uuid",
  "loan_application_id": "uuid",
  "loan_appraisal_note_id": "uuid",
  "appraisal_review_decision_id": "uuid",
  "workflow_event_id": "uuid",
  "application_status": "submitted_to_sanction_committee",
  "appraisal_status": "submitted_to_sanction_committee",
  "submission_status": "pending",
  "exception_required_flag": false,
  "submitted_by": {
    "user_id": "uuid",
    "full_name": "Credit Manager"
  },
  "submitted_at": "2026-07-10T20:30:00+00:00",
  "available_actions": []
}
```

GET is authenticated and applies the same application object-access boundary. It returns the exact
same backend-owned projection as the successful POST, including case, latest-review, and workflow
event UUIDs; it never returns submission remarks or other frozen free text. A real application
without a sanction case returns `404 NOT_FOUND`; denied scope returns `403 OBJECT_ACCESS_DENIED`.

Successful submission writes one `appraisal.submitted_to_sanction` audit record and one
`sanction_submission` workflow event with application/appraisal/case/latest-review IDs, states,
actor/time, exception flag, and request ID. Generic evidence excludes request remarks, review
comments, appraisal summaries, risk notes, and rejection text. Approval-case storage retains the
trimmed request remarks as the action reason.

## Application Witness API (004E, hardened by 004E2)

Application-scoped endpoints:

- `GET /api/v1/loan-applications/{loan_application_id}/witnesses/`
- `POST /api/v1/loan-applications/{loan_application_id}/witnesses/`

GET requires `members.witness.read` plus application object access and returns the standard list
envelope in deterministic created order. POST requires `members.witness.create` plus application
object access and accepts exactly `member_id`, `witness_name`, `address`, optional `mobile`, `pan`,
and `aadhaar`. Address is required free text up to 500 characters; a supplied mobile contains 7-15
digits after spaces are removed.

The selected member must exist, the trimmed/case-normalized witness name must match its legal or
display name, member KYC must be `verified`, and persisted shareholding evidence must include an
`active` row with `number_of_shares > 0`. Missing records return `404 NOT_FOUND`; non-shareholders
return `400 WITNESS_NOT_SHAREHOLDER`; missing/invalid identity, KYC, name, unknown, or
caller-supplied verification fields return the applicable standard 400 envelope. Malformed JSON,
arrays/scalars, missing fields, and unknown fields never escape the adapter: they return a standard
`400 VALIDATION_ERROR` envelope and write no witness, audit, or workflow row.

Successful response data contains `witness_id`, application/member IDs,
`verification_shareholding_id`, immutable verification-time `folio_number`, name, masked
PAN/Aadhaar objects, `shareholder_verified_flag: true`,
`verification_status: verified`, verifier/time, and creation time. Plaintext identities, protected
tokens, and keyed hashes are never returned or audited. Creation writes one metadata-only
`applications.witness.created` audit row and no workflow event or application-state transition.
Later shareholding folio/status/count changes or newly created holdings do not change witness read
evidence. Legacy rows whose creation audit folio does not resolve to exactly one member
shareholding expose both evidence fields as `null` rather than selecting current facts.
### Witness correction and resource actions (006Y4, closed by 006Y8)

- The collection GET additionally returns top-level six-field `actions` for `read` and `create`;
  each witness returns `version` plus six-field `actions` for `read`, `correct_contact`, and
  `correct_identity`. Contact and identity entries separately project the authority for the exact
  fields they govern; clients do not infer correction authority from field names.
- `GET/PATCH /api/v1/loan-applications/{loan_application_id}/witnesses/{witness_id}/` requires
  `members.witness.read/update` respectively and exact application object access.
- PATCH requires current positive-integer `version` and accepts only `witness_name`, `address`,
  optional `mobile`, `pan`, and
  `aadhaar`. Verification evidence/provenance fields are immutable. Invalid fields return 400;
  stale version returns `409 VERSION_CONFLICT`, both with zero domain/evidence writes.
- Verified identity correction requires a different authorised actor from the verification actor.
  Success increments version, stores protected identity, returns masked values, writes masked
  history, and emits metadata-only `applications.witness.corrected` audit evidence.
- Collection/resource action arrays always contain their entries in the standard six-field shape.
  Denied actions remain present with the exact permission, application-object, or maker-checker
  reason; projection and PATCH consume the same correction evaluation, including current version.

#### Parent authority and non-disclosure ordering (006Y16)

Witness resource GET/PATCH applies response-decision precedence in this order: required witness
permission, parent application object scope, parent absence, then child lookup. Credit Manager scope is all existing
applications whose persisted `current_stage` is `credit_assessment`; the role does not confer a
row-independent global scope for an unresolved application identifier.

Consequently, a Credit Manager with the required witness permission receives normal child lookup
semantics for an existing Credit Assessment parent, including `404 NOT_FOUND` with message
`Witness was not found.` when the child is absent. An existing application outside that domain and
a random parent UUID both stop before witness lookup with the same HTTP 403 error fact:

```json
{
  "success": false,
  "error": {
    "code": "OBJECT_ACCESS_DENIED",
    "message": "You do not have access to this loan application.",
    "details": {},
    "field_errors": {}
  },
  "meta": {
    "request_id": "<request-id>",
    "timestamp": "<timestamp>",
    "api_version": "v1"
  }
}
```

Only an actor with a separately documented application-wide scope that is independent of facts on
the unresolved row may pass parent authority and receive `404 NOT_FOUND` with message
`Loan application was not found.` for a missing parent. No current witness-correction role has that
scope. Every denied parent/child path leaves Witness, WitnessChangeHistory, AuditLog, and
WorkflowEvent unchanged.

The normal missing-child envelope after successful parent authority is:

```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Witness was not found.",
    "details": {},
    "field_errors": {}
  },
  "meta": {
    "request_id": "<request-id>",
    "timestamp": "<timestamp>",
    "api_version": "v1"
  }
}
```

If a future row-independent application-wide scope is documented, the corresponding missing-parent
envelope is:

```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Loan application was not found.",
    "details": {},
    "field_errors": {}
  },
  "meta": {
    "request_id": "<request-id>",
    "timestamp": "<timestamp>",
    "api_version": "v1"
  }
}
```

# Epic 006 authoritative workbench actions (006H4)

Eligibility, loan-limit, appraisal-note, appraisal transition, and sanction submit/read success
responses now include `data.available_actions[]` in the source §44 shape: `action_code`, `label`,
`enabled`, `disabled_reason`, `required_permission`, and nullable `required_role`. The projection is
object-, state-, permission-, and role-aware. Appraisal actions are `credit.appraisal.update`,
`revalidate_appraisal_prerequisites`, `credit.appraisal.submit_review`, `credit.appraisal.review`,
and `credit.appraisal.submit_sanction`; disabled actions remain present with a reason. Clients must
not supplement this resource projection from `/auth/me.available_actions`.
# Member create/update and identity governance (006Y)

- `POST /api/v1/members/` requires `members.member.create` and accepts the §13.2 individual-farmer
  or FPC/producer-institution payload. New members start with `membership_status =
  pending_verification`, `kyc_status = pending`, `default_status = no_default`, and `version = 1`.
- `PATCH /api/v1/members/{member_id}/` requires `members.member.update`, accepts the §13.4 contact,
  address, and name fields plus mandatory current `version`, and returns `409 STALE_WRITE` without
  writes when the version is stale.
- Verified `pan`/`aadhaar` changes through PATCH return `409 VERIFIED_IDENTITY_LOCKED`; the rejected
  attempt changes no member/history state and writes a metadata-only rejection audit.
- `POST /api/v1/members/{member_id}/reverification/` requires the same update permission, current
  `version`, at least one valid `pan`/`aadhaar`, and `reason`. Success masks history values, resets
  member KYC to `pending`, clears `rekyc_due_date`, increments `version`, and records audit/history.
- Member detail now returns `version` and exact six-field resource actions for
  `members.member.update` and `members.member.reverify_identity`. Resource actions, not `/auth/me`
  permissions alone, are authoritative for mutation UI.

## Member governance and witness UI closure (006Y2)

- Staff UI calls the 006Y member POST/PATCH/reverification endpoints and performs a canonical
  member-detail GET after successful update/reverification. It preserves backend 400/403/409
  errors and uses only the resource's update/reverification actions for profile mutation controls.
- Application Detail calls the 004E2 witness GET/POST endpoint and performs a canonical witness
  GET after successful capture. Immutable verification-time shareholding/folio evidence is rendered
  from that read response; identity values remain masked after capture.
- The former witness-correction mismatch is closed by 006Y4's versioned resource contract.

## Member Registry and approved identity change (006Y3)

- `POST /api/v1/members/{member_id}/identity-change-requests/` requires
  `members.member.update`, current `version`, a reason, and at least one valid PAN/Aadhaar. It
  persists protected proposed values and returns only request metadata; the member remains verified
  and unchanged until approval. The legacy `/reverification/` route is a compatibility adapter to
  this request operation.
- `POST /api/v1/member-identity-change-requests/{request_id}/approve/` requires the dedicated
  `members.member.identity_change.approve` permission and a different actor. It applies a pending,
  current-version request once, resets KYC to pending, clears the re-KYC due date, increments member
  version, and writes masked history/audit. Stale or repeated approval returns `409`.
- Member detail includes nullable `pending_identity_change` metadata and six-field request/approval
  actions. Duplicate PAN/Aadhaar create attempts return `400 VALIDATION_ERROR` field errors and the
  database also enforces nonblank hash uniqueness.

# Approval matrix and sanction committee configuration (007A)

- `GET/POST /api/v1/approval-matrix-rules/` and
  `PATCH /api/v1/approval-matrix-rules/{approval_matrix_rule_id}/` implement source §25.1.
  Reads require `approvals.matrix.read`; POST/PATCH require the Critical
  `approvals.matrix.manage` permission. PATCH is a supersede operation: it closes the prior row
  the day before the replacement's `effective_from` and returns a new rule id/version.
- Rule responses expose `approval_matrix_rule_id`, decision/condition, nullable inclusive amount
  bounds, `required_approver_roles`, `required_director_count`, joint-approval and register facts,
  effective range, status, and `version_number`. Overlapping amount plus effective ranges for the
  same decision/condition return `409 CONFIGURATION_CONFLICT` with no configuration, version, or
  audit writes. Invalid/non-finite amounts return `400 VALIDATION_ERROR`.
- `GET/POST /api/v1/sanction-committees/` and
  `PATCH /api/v1/sanction-committees/{sanction_committee_id}/` are the exact committee management
  paths selected for data-model §15.1. They use the same permissions and immutable supersession
  convention and return CFO/director user ids, Board meeting reference, effective range, status,
  and version.
- The approval-owned resolver interface accepts typed `decision_type`, canonical nullable
  `condition_code`, finite non-negative amount, and authoritative `decision_date`; it returns one
  immutable rule-id/version projection or stable no-effective/ambiguous/invalid-facts domain errors.
# Approval Configuration Collections and Committee Resolution (007A2)

`GET /api/v1/approval-matrix-rules/` and `GET /api/v1/sanction-committees/` use the standard
top-level paginated list envelope. They accept only positive `page` and `page_size`; `page_size` is
capped at 100 and unknown parameters return `400 VALIDATION_ERROR`. Ordering is deterministic.

Committee POST/PATCH payloads retain the 007A fields, but the three referenced active users must
carry persisted authority types `cfo`, `director`, and `director` respectively and must be distinct.
Approval-owned `resolve_sanction_committee(decision_date)` returns the immutable committee id,
version, decision date, CFO user id, and both Director user ids. No match and multiple matches have
stable `NO_EFFECTIVE_SANCTION_COMMITTEE` and `AMBIGUOUS_SANCTION_COMMITTEE` domain codes.

# Approval Configuration Maker-Checker Governance (007A3)

Rule and committee POST/PATCH payloads now require a non-blank `reason`; success returns a pending
proposal with `approval_configuration_proposal_id`, `proposal_type`, nullable `target_entity_id`,
immutable `payload`, `reason`, `status`, `version`, maker/checker ids, nullable `decided_at`,
rejection reason, and §44-shaped
`available_actions`. It does not make configuration effective.

- `GET /api/v1/approval-configuration-proposals/{proposal_id}/`
- `POST /api/v1/approval-configuration-proposals/{proposal_id}/approve/` — `{"version": 1}`
- `POST /api/v1/approval-configuration-proposals/{proposal_id}/reject/` —
  `{"version": 1, "reason": "Policy evidence incomplete"}`

Proposal detail returns `401 AUTH_REQUIRED` without a valid session and `403 FORBIDDEN` to an
authenticated user who is neither the maker, an active persisted CFO/Company Secretary checker,
nor a holder of `approvals.matrix.read`. Those participants/readers receive 200. This boundary does
not infer access from display role names and prevents unrelated users from seeing Critical change
reasons, actor ids, or action eligibility.

The checker must be active, distinct from the maker, and carry persisted `cfo` or
`company_secretary` authority. Self-decision and missing authority return
`403 MAKER_CHECKER_VIOLATION` and `403 APPROVAL_AUTHORITY_REQUIRED`; stale version returns
`409 STALE_VERSION`; terminal replay returns `409 TRANSITION_CONFLICT`; approval-time lifecycle
conflicts return `409 CONFIGURATION_CONFLICT` or `409 PROPOSAL_STALE`. Validation uses the standard
`400 VALIDATION_ERROR` field-error envelope. Approval atomically activates/supersedes and writes
separate author/approver VersionHistory plus `config.changed`; rejection changes no effective row.

# Approval-case enrichment from appraisal (007B)

`POST /api/v1/loan-applications/{loan_application_id}/approval-cases/` requires an authenticated
holder of `approvals.case.create` with object access to the application. It accepts exactly the
source §25.2 fields `approval_type = sanction`, an `amount` equal to the reviewed appraisal's
recommended amount, a non-blank `reason_for_approval`, and boolean `force_exception_route`.
When the frozen assessment requires an exception or the caller forces that route, the request also
requires a distinct non-blank `business_reason` and may include a string `risk_assessment`.
An assessment-required route has canonical `exception_type = exceeds_loan_limit`; a forced
within-limit route must explicitly name `stage_bypass` or `waiver` so the register never claims a
limit breach that did not occur.

The adapter never creates a row. It enriches the unique pending shell created by the §24.5 sanction
submission or returns `404 NOT_FOUND`. It derives application/appraisal identity from that shell,
uses the latest immutable review date, and consumes the stored verified loan-limit assessment's
condition and policy provenance. Missing/stale provenance is `409 INVALID_STATE_TRANSITION`;
missing or ambiguous effective approved configuration uses the resolver's stable 400 code.

Success returns the existing submission projection plus immutable `approval_type`, amount,
rule/committee ids and versions, decision date, concrete `required_approvers`, empty
`excluded_approvers`, related-entity facts, reason, canonical exception condition, complete matrix
and committee projections, loan-limit provenance, and case `version`. An identical repeat returns
the same projection without writes. A conflicting repeat or decided case returns 409. Later matrix,
committee, pending-proposal, or losing-proposal changes never rewrite the stored projection.

# Approval-case queue and detail reads (007C)

`GET /api/v1/approval-cases/` requires `approvals.case.read` and accepts only `current_status`,
`approval_type`, `assigned_to_me`, `page`, and `page_size`. It returns the standard top-level
pagination envelope. `approval_type`, when present, is exactly `sanction`; `current_status`, when
present, is exactly `pending`, `approved`, `rejected`, `returned_for_clarification`, or
`blocked_by_conflict`. Unknown values return `400 VALIDATION_ERROR` rather than an empty successful
page. `assigned_to_me=true` includes only complete version-2-or-later 007B routing
snapshots where the caller remains in `required_approvers`, is absent from `excluded_approvers`,
has no immutable `approval_actions` row, and the case is still pending. Missing/default snapshot
facts never fall back to amount, the current matrix, or the current committee.

`GET /api/v1/approval-cases/{approval_case_id}/` also requires `approvals.case.read`. Any global
object scope must be persisted separately; the permission alone is not global scope. A complete
routed case is visible when its immutable `required_approvers` snapshot names the caller (including
the caller's own acted history), when a Credit Manager owns the case submission or passes the
existing application object-scope decision, or when the caller's active role has an active persisted approval-case
read-scope grant. The bounded grant types are `legal_readonly`, `audit_readonly`, and
`management_readonly`; the default catalogue seeds only Company Secretary legal read-only and
Internal Auditor audit read-only grants. The broad `management_readonly` permission, role display
text, and caller query flags never imply a grant. Unassigned Directors, unrelated case makers, and
arbitrary custom-role permission holders receive an empty scope-filtered collection
(`total_count = 0`) and direct detail returns `403 OBJECT_ACCESS_DENIED`. A non-reader receives
`403 FORBIDDEN`; an incomplete or internally contradictory snapshot is not a public case and
returns `404 NOT_FOUND`. Reads and denials write no audit or workflow evidence.

Object scope is applied before pagination and count calculation. `assigned_to_me=true` is the
narrower queue filter: the caller must additionally be pending, unexcluded, and without an
immutable action. The ordinary collection does not bypass object scope and keeps acted cases in
the assigned actor's readable history. Read-only role grants and Credit Manager ownership never
create an assignment, enable an action, or bypass its action-specific permission. The collection
selector narrows candidates in the database by persisted role scope, immutable approver candidacy,
or Credit Manager ownership before the remaining JSON coherence validation runs.

The selector's indexed `routing_snapshot_is_coherent` and attributable-reader projection are
updated only through the explicit approval-owned projection interface. Case creation, workflow
linkage, enrichment, and actions/abstention invoke it atomically; an ordinary approval-case or
appraisal save has no hidden cross-table side effect. A later live appraisal mutation cannot rewrite
the coherence or reader index of a frozen historical cycle. The reader projection contains only
original routed actors, current effective replacements, and actors with an immutable action. It
narrows the database scan, but the approval-owned frozen-validity and actor-scope decision runs
over every narrowed candidate before collection/register filters, counts, page normalization,
`LIMIT/OFFSET`, or serialization. Detail, action, sanction-decision, and register reads execute the
same decision and never trust the projection as read or action authority.

For the approval-case collection, coarse actor scope plus valid approval type, status, and
assignment/index filters run before canonical Python validation. Every remaining candidate still
passes through the single frozen-validity/read-scope decision before totals, pages, or rows are
produced. A stale true projection can therefore add validator work but cannot create a page hole or
inflate `total_count`; unrelated actors, types, and statuses are not materialized for validation.

Detail returns stored authority/provenance (`approval_matrix_rule_id` and version,
`sanction_committee_id` and version, `decision_date`, ordered required/excluded approvers,
matrix/committee/loan-limit snapshots, distinct `reason_for_approval` and `exception_reason`, and
case `version`). Per-approver `decision`/`acted_at` are
read from the immutable source §15.4 `approval_actions` ledger; 007C creates no action records.

The nested `review_facts` object is frozen into each enriched approval cycle. New cycles use
`approval-review-v3`, which includes credit-owned snapshot provenance; borrower member id,
application reference, name, and type; and reviewed sanction terms (tenure, interest type, and
security summary) in addition to the review sections below. The exact pre-007O
`approval-review-v2` shape remains actor-scoped/readable under its original immutable validation
rules, but it is historical-only: it is never reinterpreted as carrying v3 terminal facts.
Unknown schemas and malformed v3 packages remain nondisclosing. Reads and terminal writes never
reconstruct missing facts from current owning rows:

- `eligibility` and eligible amount come from the appraisal-owned frozen eligibility/loan-limit
  snapshots.
- requested amount, purpose, and documentation/completeness status come from the owning loan
  application.
- borrowing history, recommendation amount, and sanction terms come from the owning appraisal
  note at review-package creation.
- risk ratings/mitigation come from the owning risk assessment.
- `source_references` links the application, appraisal, eligibility, and loan-limit owner APIs.

Changing current matrix/committee rows cannot change queue membership, stored provenance, or
action assignment for an existing case.

Authority history returns formal display names only from the routed immutable approver snapshot or
the action's immutable action-time display name. User ids remain the attribution identity. A later
user-profile rename cannot change case history or a generated register; a legacy action whose name
is unavailable from both immutable owners returns `full_name: null` rather than reading the current
user profile.

Every list/detail item also returns `workbench_summary`, derived only from the frozen review package,
frozen matrix/case flags, immutable action ledger, and approval-case timestamps. It contains
`borrower_name`, `member_type`, requested/recommended/eligible amounts, `approval_path`, exception
and related-party booleans, `risk_rating`, `submitted_at`, `current_decision_status`, and nullable
`pending_age`. A pending case with an immutable approval reports `partially_approved`; otherwise the
decision status matches the case. `pending_age` is labelled `Elapsed pending time` and includes
server-projected elapsed seconds/display only while pending. It does not claim a target or breach
before the later workflow-TAT policy boundary exists.

The S21 frontend sends `approval_type=sanction` on every collection request. The assigned pending
queue additionally sends `current_status=pending&assigned_to_me=true`; historical filters send their
exact status without assignment. Every request also sends explicit `page` and `page_size=20`; S21
renders `pagination.total_count`, exposes the existing previous/next pattern, resets to page one on
filter changes, and replaces rows plus pagination from the same response. Collection failure clears
both. The shared authenticated paginated client accepts success only when `data` is an array and all
six top-level pagination fields are present, non-negative/in-range, and internally consistent; it
returns `MALFORMED_RESPONSE` rather than fabricating empty pagination. S22 renders every immutable `approval_actions` actor, role,
decision/abstention, comment/reason, and acted-at confirmation separately from required/effective
authority.

Routability is one approval-owned validation contract shared by list, detail, action,
sanction-decision, and register
seams. Case/application/type/amount/decision/exception facts must agree with the stored matrix;
rule and committee ids, versions, and dates must match; the snapshot must contain exactly the
stored CFO and required distinct Directors with unique ids; required roles/director count and
joint/register facts must be complete; and the loan-limit assessment/application/exception/policy
provenance must be internally complete. The credit-owned enrichment interface validates the locked
appraisal and loan-limit source once, then freezes the complete provenance and `review_facts` on
the case. Existing-cycle validation never compares those facts with the mutable live appraisal or
a later revision. Invalid or contradictory frozen snapshots are hidden and non-actionable without
writes or count leakage; live appraisal, rule, committee, or user membership is never queried to
repair them.

The §25.2 enrichment success projection now includes source-required `current_status`. Enrichment,
list, and detail compose the same canonical immutable routing projection (status, rule/committee,
decision date, required/excluded authority, and loan-limit provenance). Detail adds immutable
decision history, review read-throughs, and caller-specific actions; existing submission fields
remain backward-compatible additions.

For a case whose frozen projection requires General Meeting evidence, detail also includes the
resource action `record_general_meeting_approval`. The backend enables it only when the actor has
canonical case scope, belongs to the §19.4 legal audience, and holds
`approvals.general_meeting.record`, `approvals.case.read`, and `documents.file.download`; otherwise
the same action is returned disabled with a reason. Ordinary cases omit this inapplicable action.
The frontend may intersect the enabled resource action with `/auth/me` permissions for usability,
but a global permission never creates or enables the action.

An enrichment replay is exact only when the locked reviewed decision date and recommended amount,
assessment/application ids, exception flag, calculation rule, policy id/name, and calculation time
equal the frozen case provenance. Any changed reviewed or credit fact returns stable
`409 INVALID_STATE_TRANSITION` and leaves case/action/audit/workflow ledgers unchanged. A later
effective governed configuration version does not rewrite an otherwise coherent historical case.

# Approval-case actions and sanction decision creation (007D)

`POST /api/v1/approval-cases/{approval_case_id}/approve/`, `reject/`, and
`return-for-clarification/` accept exactly optimistic integer `version` and optional `comments`;
comments are mandatory and non-blank for reject/return. The caller must hold the action-specific
permission and remain a pending, unexcluded actor in the coherent immutable case snapshot.
Permission failure is `403 FORBIDDEN`, missing object scope is `403 OBJECT_ACCESS_DENIED`, stale
version is `409 STALE_VERSION`, and acted/closed/excluded state is `409 TRANSITION_CONFLICT`.
The submitted `version` must be a positive JSON integer; booleans, zero, negative values, strings,
missing values, and unknown request fields return `400 VALIDATION_ERROR` without writes. Approve
permits omitted/blank comments; reject and return require a non-blank string.

For a readable v2 historical case, approve and reject are returned disabled with the reason
`Frozen terminal facts are unavailable. Return for clarification and complete a new independent
review cycle.` A direct approve/reject attempt returns
`409 TERMINAL_FACTS_REMEDIATION_REQUIRED` with exact zero-write semantics. Return remains available
to an otherwise eligible actor; correction, a fresh independent Credit Manager review, and normal
resubmission create a new v3 cycle without rewriting the v2 cycle.

Success returns the §25.5 action identifiers/status/sanction flags merged with the canonical 007C2
case detail projection. Collection, detail, and action responses now compose the same history-aware
projection: route provenance is immutable, while each required approver's `decision`/`acted_at` and
the caller's `available_actions` reflect the action ledger immediately. Each action increments case `version`, creates one immutable §15.4 row,
and immediately disables every action for that actor. Partial joint approval remains pending. Final
approval atomically closes the case, advances the application to `approved_by_sanction_committee`,
and creates the unique per-application §15.5 sanction decision. Reject advances the application to
`rejected_by_sanction_committee`; return restores the application to `appraisal_reviewed` and the
appraisal to editable `draft` so clarification can be supplied.
Every successful action writes attributable audit/workflow evidence. Each terminal outcome crosses
the communication-owned internal adapter in the same transaction, persisting one source §24.2
`pending` email `Communication` snapshot, one linked in-app notification to the persisted
`credit_assessment` team, and a metadata-only communication audit. Any adapter persistence failure
rolls back the action, case/application outcome, sanction, register, workflow, communication,
notification, and audits. Application, appraisal, and case source states are re-evaluated through
the shared transition guard after locking and before mutation. As delivered by 007H, an approved
or rejected terminal action also freezes exactly one Credit Sanction Register row in this same
transaction; partial approval, return, and conflict-blocked outcomes do not.

# Exception approval and generated Exception Register (007F)

An exception-routed §25.2 enrichment requires both `approvals.case.create` and
`approvals.exception.create`. It atomically creates exactly one
`exception_register_entries` row for that approval case/cycle. The canonical type is
`exceeds_loan_limit`; the bounded future-caller vocabulary is `stage_bypass` and `waiver`, and an
unknown type is rejected. The entry copies the request's distinct `business_reason` and optional
`risk_assessment`, links the loan application and approval case, and begins `pending`. An ordinary
within-limit route creates no entry. Exact enrichment replay creates no duplicate or evidence.

The same request may include optional `supporting_document_ids` as an ordered list of at most 20
distinct UUIDs. The documents owner validates every supplied id through public-upload provenance,
exact application attribution, legal category, matching sensitivity, document permission, role,
workflow, and object scope before the locked enrichment writes. Approvals stores only the returned
immutable display projection (`document_id`, file name, MIME type, size, sensitivity, upload time)
on the exact register entry/cycle and never queries `DocumentFile`. Empty/omitted evidence freezes
an empty list. Exact ordered-id replay is zero-write; any changed ordered list after routing returns
the existing immutable-snapshot `409` conflict.

Inside the locked approval-action transaction, partial approval leaves the entry pending. Final
approval changes it to `approved`; rejection changes it to `rejected`; both copy the case
`closed_at`. Return-for-clarification and `blocked_by_conflict` also copy the case closure time but
remain `pending`, because source data-model §15.7 defines no additional status. Denied conflicted
actions never mutate the entry. Creation and outcome projection write attributable
`exception_register.*` audit plus `exception_register` workflow evidence.

`GET /api/v1/exception-register/?status=&exception_type=&page=&page_size=` requires
`approvals.exception_register.read`, accepts only the source status/type vocabulary, and returns
the standard pagination envelope. It is generated/read-only: mutation methods are not routed.
Object scope delegates to the canonical approval-case selector before count and pagination. Each
row includes register/application/case ids, `cycle_number`, type, description, business/risk facts,
entry/case statuses, conflict reason, timestamps, `authority_applied_summary`, and canonical
`route_approvers`, `required_approvers`, and complete `approval_actions`. Reads never re-run
conflict replacement or consult live committee membership. Each row also includes
`supporting_documents` with the frozen metadata above. Register visibility and metadata never grant
download; S25 exposes no download control unless a separate document resource independently
authorises an action.

As of 007Q each new row also freezes `borrower_name`, the routed reviewed amount as nullable
`financial_impact` (A-096), and `requested_by = {user_id, full_name}` at exception creation.
`decision_date` is the immutable terminal case closure date or null while pending. Later member,
application, or requester-profile edits cannot change those response facts. Legacy rows whose
pre-007Q evidence cannot be proven expose the unavailable fact as null rather than reconstructing
it from a live owner.

The nullable `loan_account_id` is currently a UUID reference, not a foreign key to the tracer app's
synthetic demo account. A protected FK is deferred to the production finance loan-account owner
(A-084); exception entries created before sanction naturally carry no loan account.

## Exception predicate and coherence closure (007F2)

For a non-forced route, the reviewed `recommended_amount` must exceed the frozen
`final_eligible_loan_amount` exactly when the frozen `exception_required_flag` is true. Either
contradiction returns `409 INVALID_STATE_TRANSITION` before matrix/committee resolution and leaves
the existing submission shell, routing, register, audit, workflow, and communication ledgers
unchanged. `force_exception_route = true` is the only within-limit exception path and still requires
truthful `stage_bypass` or `waiver` type plus a non-blank business reason.

`reason_for_approval` belongs to the sanction case and becomes the sanction decision reason.
`business_reason` belongs to the generated Exception Register; the case freezes it separately as
`exception_reason`. These independently authored reasons are not required to be equal. An
exception-conditioned routing snapshot is coherent only when the same-case register row matches
the case/application, `exception_reason`, truthful exception type, optional risk shape, frozen
amount/limit predicate, the `exceeds_permissible_limit` matrix condition, two-Director authority,
and `register_required = exception_register`. Exact replay is zero-write; changed reason, risk,
type, amount, or frozen provenance conflicts without rewriting or hiding the original case.

# Returned approval cycles and resubmission (007D3)

Every sanction approval case now carries positive `cycle_number`, immutable
`appraisal_review_decision_id`/`appraisal_revision`, and frozen `review_facts`. The database enforces
unique `(loan_application, cycle_number)` and at most one pending cycle per application. Existing
cases migrate to cycle 1; collection, detail, submission, enrichment, and action success projections
all expose `cycle_number`.

A returned case is closed history and never becomes assigned or actionable again. Its case,
approver/action snapshot, frozen appraisal/configuration facts, audit/workflow, and communication
evidence remain attached to that exact cycle. The maker may PATCH the returned draft through the
existing appraisal boundary; only a non-empty `appraisal.updated` changed-field ledger after the
return counts as correction. A no-op PATCH does not create revision authority.

The existing `POST /api/v1/loan-applications/{loan_application_id}/submit-to-sanction-committee/`
boundary creates cycle N+1 only when the latest prior cycle is `returned_for_clarification`, the
appraisal has a later attributable correction ledger, and the latest immutable Credit Manager
`reviewed` decision follows that correction. Pending, approved, rejected,
uncorrected, stale-review, or otherwise incompatible submissions return
`409 INVALID_STATE_TRANSITION` without a new case or sanction-submission evidence. The standard
application -> appraisal -> approval-case lock order plus database uniqueness serializes competing
resubmissions to one new shell/evidence set.

Cycle N+1 is enriched from its own current reviewed appraisal/configuration facts. Its action ledger
starts empty, so a user who acted in cycle N may independently act again when snapshotted in cycle
N+1. Final approval creates the application-unique sanction decision only from the latest pending
cycle; prior returned actions never count toward joint approval.

# Conflict-of-interest exclusions and abstention (007E)

Approval enrichment evaluates source conflict declarations plus frozen application/appraisal maker
facts for that exact `cycle_number`. It leaves ordered `required_approvers` unchanged and writes
unique `excluded_approvers` objects containing `user_id`, `conflict_code`, and non-blank `reason`.
Director/relative declarations set `general_meeting_evidence_required = true`. A frozen same-role
committee alternate may fill an excluded Director slot; the stored matrix role/count never shrinks.
If no frozen alternate can preserve required CFO/Director authority, the case becomes
`blocked_by_conflict`, closes without a sanction decision, and exposes `conflict_block_reason`.

An excluded actor has limited case-detail/history access only: they never enter
`assigned_to_me`, never receive an enabled action, and no permission or live committee membership
widens that scope. Every attempted approve/reject/return returns `409` with the exact source body:

```json
{
  "success": false,
  "error": {
    "code": "CONFLICTED_APPROVER_NOT_ALLOWED",
    "message": "This user is marked as conflicted for the approval case and cannot approve it.",
    "details": {
      "approval_case_id": "uuid",
      "conflict_reason": "Borrower is relative of Director."
    },
    "field_errors": {}
  }
}
```

The denial adds one `approval_case.conflicted_action_denied` audit row naming the exact case,
cycle, attempted action, reason, actor, request, IP, and user agent. It creates no ApprovalAction and
changes no case/application/appraisal/sanction/workflow/communication ledger.

`POST /api/v1/approval-cases/{approval_case_id}/abstain/` accepts exactly positive integer
`version` and mandatory non-blank `comments`. It uses the existing approval authority permission
and immutable action ledger with decision `abstained`, increments case version, and adds a
`self_declared_abstention` exclusion. The case stays pending when frozen alternate authority can
satisfy the matrix; otherwise it closes as `blocked_by_conflict` and notifies the Credit Assessment
team through the communication adapter. Prior-cycle exclusions/abstentions never populate a later
cycle; every enrichment recomputes from that cycle's frozen facts.

# Conflict authority, history projection, and scope closure (007E2)

Conflict replacement fills frozen role slots with distinct users. A user can occupy at most one
effective CFO/Director slot; a two-Director route with either Director excluded therefore blocks
when the frozen committee has only one remaining distinct Director. `conflict_block_reason` names
the exact missing CFO or Director authority, the case closes atomically, and no sanction is
created. `required_approvers_json` remains immutable route provenance.

Collection, detail, action success, and historical-cycle reads share these authority facts (the
§25.2 enrichment response preserves its backward-compatible raw `required_approvers` shape):

- `route_approvers`: the unchanged ordered matrix/committee route snapshot.
- `required_approvers`: the currently executable distinct actors with `role_code`, `user_id`,
  `full_name`, nullable `decision`/`acted_at`, and `replacement_for_user_id` only when the actor
  replaces an excluded original.
- `approval_actions`: every immutable action with `approval_action_id`, role/user/name, decision,
  comments, acted time, and replacement attribution when applicable.

These three fields are identical in collection, detail, and the case portion of action responses;
only caller-specific `available_actions` and the action endpoint's top-level result fields differ.
An excluded original may retain COI-005 history access only because it is an original, effective,
or already-acted cycle participant. Frozen committee candidacy, an unused-alternate declaration,
or action permission alone grants no row, count, detail, queue, or write scope. An unused alternate
therefore receives `total_count: 0` and direct `403 OBJECT_ACCESS_DENIED`.

Active borrower and Director-relative declarations set
`general_meeting_evidence_required = true` even when the related Director/committee member is not
assigned to this case. Material-interest and maker-checker facts alone do not set the flag.
Exclusions remain limited to frozen authority candidates, and database validation rejects empty or
whitespace-only declaration reasons.

# General-meeting evidence and final-sanction gate (007G)

`POST /api/v1/loan-applications/{loan_application_id}/general-meeting-approval/` requires
`approvals.general_meeting.record`, `approvals.case.read`, canonical object scope to the latest
routed approval cycle, and `documents.file.download`. The case's immutable
`general_meeting_evidence_required` flag must be true. The request accepts only:

```json
{
  "related_party_type": "director_relative",
  "related_party_user_id": "uuid-or-null",
  "relationship_description": "Borrower is a relative of a Director.",
  "meeting_date": "2026-07-15",
  "notice_document_id": "uuid",
  "minutes_document_id": "uuid",
  "resolution_document_id": "uuid",
  "approval_status": "pending | approved | rejected"
}
```

`related_party_type` is exactly `director`, `director_relative`, or `committee_member`.
Description and ISO date are mandatory. Notice, minutes, and resolution must be three distinct,
existing document files resolved through the documents module's reference-authorization interface.
Each file must have immutable `documents.file.uploaded` provenance from the public upload path,
`related_entity_type = application`, the exact loan-application id, category `legal`, and sensitivity
matching one of the document model's source-defined levels (`public`, `internal`, `confidential`, or
`restricted`). The approval owner supplies a typed reference context only after the latest routed
case has canonical object access and its immutable related-party evidence flag proves the
`related_party_sanction_case` workflow scope; the documents owner combines that decision with each
file's provenance and the source §19.4 legal audience (Compliance Team, Company Secretary, Credit
Manager, or an attributable case approver). Audit-only or generic case read scope is not legal-file
reference authority even if the global permissions are granted. Missing, cross-application,
unattributed, wrong-category, unsupported/mismatched-sensitivity, and otherwise inaccessible files all return the same nondisclosing
`400 VALIDATION_ERROR` text on each denied request field. Missing record/document permission returns
`403 FORBIDDEN`; missing case scope returns `403 OBJECT_ACCESS_DENIED`; a non-related-party cycle
returns `409 INVALID_STATE`. Denial creates no meeting/audit/workflow/case/exception mutation and
never emits a `documents.file.downloaded` audit.

Success returns the standard envelope with the request fields plus
`general_meeting_approval_id`, `recorded_by_user_id`, `recorded_at`, and nullable
`supersedes_general_meeting_approval_id`. Exact replay returns the existing id with no audit,
workflow, or row write. A changed payload creates a new immutable row whose `supersedes` link
names the prior unsuperseded application record; it never updates the prior row. Creation writes
`general_meeting_approval.recorded`; a changed outcome writes
`general_meeting_approval.status_changed`; other changed evidence writes
`general_meeting_approval.superseded`. Each real write has matching
`general_meeting_approval` workflow evidence.

The locked approval action transaction evaluates this gate only after object scope, version,
conflict, assignment/action permission, and distinct effective authority establish that an
`approve` action would be final. Missing, pending, and rejected current evidence return 409 with
codes `GENERAL_MEETING_EVIDENCE_REQUIRED`, `GENERAL_MEETING_APPROVAL_PENDING`, and
`GENERAL_MEETING_APPROVAL_REJECTED`. Details contain `approval_case_id`, `cycle_number`, and the
same nullable `general_meeting_approval` object used by case readers. These denials insert no action
or sanction and do not close/project an Exception Register entry. A conflict still returns the
earlier canonical `CONFLICTED_APPROVER_NOT_ALLOWED` contract.

While an evidence-required cycle is `pending`, collection, detail, action success, and final-gate
details expose the application's current unsuperseded record as nullable `general_meeting_approval`;
the object has `evidence_scope = current_pending`. Successful final approval, rejection, return for
clarification, and an abstention that closes the case as `blocked_by_conflict` freeze whichever
current record exists on that exact cycle (final approval still requires `approved`; other terminal
outcomes do not). Returned and terminal readers expose only that frozen
record with `evidence_scope = cycle_frozen`, beside unchanged `route_approvers`,
`required_approvers`, and `approval_actions`. Later application-level supersession cannot change
historical case or register references. A later pending cycle resolves the then-current
unsuperseded application record independently. §25.11 success remains the source record shape
without `evidence_scope`; the scope discriminator belongs to case/gate projections.

# Sanction decision and Credit Sanction Register reads (007H/007O)

`GET /api/v1/loan-applications/{loan_application_id}/sanction-decision/` requires
`approvals.sanction.read`. It returns the source §25.8 decision shape: id, decision, sanctioned
amount/tenure, interest type/value, repayment date, penal rate, `charges`, security summary,
conditions precedent, and decision reason. It returns `404 NOT_FOUND` when no sanctioned decision
exists, including before terminal approval and after rejection. A-079 remains binding: numeric
rates, repayment date, and penal rate are nullable, charges are `{}`, and the blank conditions
snapshot is projected as `null` until an approved owner supplies those facts. Sanctioned amount,
tenure, interest type, and security summary are copied exclusively from the canonically validated
routed `review_facts`; terminal creation never reads their mutable appraisal-note counterparts.

Permission and row scope are independent. The endpoint first delegates to the approval-owned
coherent-case/read-index selector and revalidates the canonical case decision, then looks up the
immutable approved-cycle decision. Original, effective, conflicted, or acted historical approvers can read
their attributable cycle. An actor with only `approvals.sanction.read`, including an unused
committee Director, receives nondisclosing `403 OBJECT_ACCESS_DENIED` for an unrelated approved
application. A caller with case object scope but without the endpoint permission receives
`403 FORBIDDEN`. Persisted `legal_readonly`, `audit_readonly`, or `management_readonly` grants can
provide case scope only when the caller separately holds the sanction permission; they never grant
approval actions or document access. The deliberate `404 NOT_FOUND` contract still applies when no
sanction decision exists, including before approval and after rejection.

`GET /api/v1/credit-sanction-register/?financial_year=FY2026-27&decision=sanctioned&page=1&page_size=20`
requires `approvals.sanction_register.read` and returns the standard list/pagination envelope.
`decision` is exactly `sanctioned` or `rejected`; `financial_year` is canonical `FYyyyy-yy` and
uses the April 1 inclusive / following April 1 exclusive window (A-086). Page defaults to 1,
page size defaults to 20 and is capped at 100. Unknown parameters or invalid filter values return
`400 VALIDATION_ERROR`. The collection is generated/read-only: POST is method-denied and there is
no row detail/update/delete route. The slice's named readers—CFO and Director committee members,
Company Secretary, and Internal Auditor—receive this read grant in the canonical role seed;
possession of other approval/case permissions does not imply register access.

The collection delegates to the same approval-owned coherent-case/read-index selector before
financial-year or decision filters, ordering, `total_count`, page-bound normalization, and row
serialization. Consequently an original/effective/conflicted/acted Director sees only attributable
cycles and cannot infer unrelated decisions from empty pages, totals, total pages, or filter
results. Persisted legal/audit/management readers see exactly the sanction cases covered by their
active role grant, but only when they also hold `approvals.sanction_register.read`. Register
permission does not become global object authority and grants neither case actions, sanction
decision permission, document-reference authority, nor document download. The selector—not
`routing_snapshot_is_coherent`, register permission, Exception Register presence, or evidence
metadata—is the object-authority source.

A later direct appraisal save or public return/correction/re-review changes only the new credit
owner state. It cannot hide, rewrite, or reattribute an earlier enriched cycle. Pending case
detail/queue/actions, returned-cycle history, terminal case detail, the immutable sanction
decision, and the generated register row continue to use that cycle's byte-for-byte
`loan_limit_provenance` and `review_facts`. A new approval cycle freezes its newly reviewed facts
independently. Conversely, a malformed frozen case is removed before every count/page and returns
nondisclosing detail/action/decision results even when its stale projection flag/index remains true.

Every approved or rejected terminal case creates exactly one immutable
`credit_sanction_register_entries` row in the locked approval action transaction. Approved rows
link the §15.5 sanction decision; rejected rows deliberately keep that link/amount null rather than
inventing a sanction decision. The row also stores the exact terminal `sanction_approval` workflow
event, a byte-for-byte `source_review_facts_json` copy of the validated routed package (including
purpose and risk), and one attributable `credit_sanction_register.created` audit. Stale/closed
retries cannot duplicate the one-to-one case row. Partial approvals, returns, conflict-blocked
cycles, malformed frozen packages, and general-meeting gate denials create no row.

The source register fields and their frozen sources are:

| Response field | Frozen source |
|---|---|
| `entry_number` | immutable system-generated `CSR-<UUID>` formal number (A-096) |
| `application_number` | routed review package's application reference |
| `borrower_name` | routed review package's borrower name |
| `borrower_type` | routed review package's borrower type |
| `folio_number` | routed review package's member folio; null only for unproven legacy packages |
| `loan_type` | routed review package's requested loan type; null when honestly unavailable |
| `purpose` / `risk` | byte-for-byte values in the row's immutable `source_review_facts_json` |
| `requested_amount` | routed review package's requested amount |
| `eligible_amount` | routed review package's verified eligible amount |
| `recommended_amount` | routed review package's reviewed recommendation |
| `sanctioned_amount` | linked sanction decision; null for rejection |
| `approval_authority` | case's canonical effective required-authority/action snapshot |
| `approver_names` | ordered routed/action-time immutable display identities for that case/cycle |
| `approver_decisions` | each immutable action's user id, frozen display identity, role, decision, comment, and time |
| `approval_date` | terminal case closure date |
| `decision` | terminal case outcome mapped to `sanctioned`/`rejected` |
| `reasons` | case approval or rejection reason |
| `rejection_reason` | rejected terminal reason; null for sanctioned rows |
| `conditions` | immutable sanction-decision conditions; null under A-079 when unavailable |
| `communication` | exact terminal team communication id/status/sent time; pending with null sent time until delivered |
| `exception_reference` | that case's one-to-one 007F row: id/type/business reason/status/cycle |
| `conflict_abstention_details` | that case's frozen exclusions plus attributable abstention action |
| `general_meeting_approval_reference` | that case's frozen 007G row: id/outcome/date/party/user/document metadata ids |

The terminal communication is created first inside the same locked transaction and copied into the
register before commit; an adapter or register failure rolls both back. The response additionally includes register/case/application/sanction/workflow ids and
`recorded_at`. Register permission never grants document download: the three general-meeting
document values are metadata ids only, and the document module retains its own permission and
sensitivity checks. No template/Annexure code is stored or projected because OC-002 still leaves
the Annexure K label conflicted (A-087).

Pre-007O/pre-007Q register rows remain actor-scoped and readable even when
`source_review_facts_json`, `terminal_facts_json`, approver arrays, or communication facts are
empty. Unavailable folio, loan type, purpose, risk, rejection, conditions, and communication values
are explicit `null`; unavailable approver collections are `[]`. Stored borrower/application/
amount/reason values remain as recorded. Serialization never repairs an old row from live
application, member, appraisal, user, or communication records.

# Approval registers and matrix frontend consumption (007J)

`RegistersHub` consumes S23 only from `GET /api/v1/credit-sanction-register/` and S25 only from
`GET /api/v1/exception-register/`. Each filter or page change replaces the rows and pagination
object with that endpoint's latest actor-scoped response. The client does not combine the two
collections, recover hidden rows from case/detail APIs, retain an earlier total, calculate approval
authority or money, or turn case/application/document metadata ids into actions or downloads.

The S71 matrix panel consumes `GET /api/v1/approval-matrix-rules/?page=1&page_size=100` and renders
active, inactive, and retained superseded versions as returned. Each rule additionally projects
display-ready `authority_summary` and numeric `minimum_approver_count` from the approvals
configuration owner; React renders these facts verbatim and does not recompute role or Director
cardinality. A holder of
`approvals.matrix.manage` may submit a complete successor through
`PATCH /api/v1/approval-matrix-rules/{approval_matrix_rule_id}/`; success is a pending governed
configuration proposal, not an immediate edit. The active rule remains unchanged until a distinct
active CFO or Company Secretary approves the proposal through the existing 007A3 boundary.

Register export remains deferred to 012B/012C. The existing `Export Register` action is visible
only with canonical `reports.export`; in 007J it displays an explicit deferred-state notice and
makes no network request, creates no file, and does not imply broader register visibility. This
interim behavior must be replaced, not extended, when the export-job contract lands.

As of 007N, the register/matrix feature service delegates bearer/session headers, request ids,
standard envelope and field-error parsing, malformed-response handling, and pagination extraction
to the shared authenticated frontend client. The feature boundary owns only its exact endpoints,
query filters, successor payload, and typed DTOs.

As of 007Q S23 and S25 render each result as the existing register card/detail composition so the
complete source facts, approver comments/times, and supporting-file metadata are reviewable without
horizontal off-screen evidence. Both still use the same strict paginated transport and atomic
row/pagination replacement. Metadata ids never create a download control.

# Document-template catalogue and immutable successors (008A)

`GET /api/v1/document-templates/` requires `documents.template.read` and returns the standard
list envelope. It accepts only `document_type`, `borrower_type`, `approval_status`, `page`, and
`page_size`; unknown parameters return `400 VALIDATION_ERROR`. `borrower_type` is nullable and
accepts the repository/source variants `individual_farmer`, `fpc`, or `fpo`; the literal `null`
filters the generic variant. `approval_status` is exactly `draft`, `approved`, or `retired`. Page
defaults to 1, page size defaults to 20 and is capped at 100.

`POST /api/v1/document-templates/` and
`PATCH /api/v1/document-templates/{document_template_id}/` require
`documents.template.manage`. Both accept a complete object:

```json
{
  "template_code": "annexure_e_term_sheet_v1",
  "template_name": "Term Sheet",
  "document_type": "term_sheet",
  "borrower_type": "individual_farmer",
  "template_version": "1.0",
  "template_file_id": "uuid-or-null",
  "merge_fields": ["borrower_name", "loan_amount"],
  "approval_status": "approved",
  "effective_from": "2026-04-01",
  "effective_to": null
}
```

Required values are code, name, document type, version, approval status, and effective-from.
Merge fields must be a list of unique nonblank names. Effective-to cannot precede effective-from.
Template code is globally unique; document type, borrower variant, and version are unique together;
approved effective ranges for the same document type/borrower variant cannot overlap. As of 008A2,
every create/successor locks a unique non-null document-type/borrower-variant identity row before
checking replay, uniqueness, and effective intervals, including when no template row exists yet.
Thus concurrent overlapping first versions persist one winner/evidence set; valid non-overlapping
identities and variants remain independent.

A non-null template file crosses the documents-owned template-source reference decision. The upload
ledger must be singular and exactly match the immutable file metadata, carry
`document_category=template_source`, `related_entity_type=global`, no related entity id, and one of
the source-defined sensitivity values. The actor must independently hold
`documents.template.file_reference`. Missing rows/ledgers, corrupt or duplicate ledgers,
application/loan ownership, invalid sensitivity, unrelated actors, manage/read permission, and
download permission alone all return the same nondisclosing zero-write validation error. Reference,
template read/manage, upload, and file download remain separate authorities; reference checks emit
no download audit and responses expose no storage descriptor.

PATCH never updates the addressed row. It locks that row and creates its sole immutable successor;
the complete payload must carry a new code/version. Exact POST or PATCH replay returns the original
result with no additional template, audit, or version-history write. Each real creation writes one
attributable `documents.template.created` or `documents.template.successor_created` audit plus one
`document_template` version-history row containing old/new version, status, effective dates,
template-file id/name, actor, and request metadata.

Success data contains `document_template_id`, the request fields, nullable
`template_file_name`, and `created_at`. It deliberately contains no storage key, download URL,
enabled/available action, generated document, or Annexure routing fact. The unresolved J/K/L
lettering remains descriptive source metadata and does not affect identity, selection, or routing.

008A2 also exposes one backend resolver for 008B: repository member type `individual_farmer`
resolves to the Individual template variant, while `fpc`, `producer_institution`, and unknown member
types return a configuration-required validation result. No implicit FPO mapping or cross-variant
selection is permitted until governance confirms it. Catalogue filtering/pagination now lives in
the documents selector, and write modules receive transport-neutral request metadata rather than a
raw HTTP request; the public routes, envelopes, fields, strict filters, and page bounds are unchanged.

## Loan document generation and metadata list (008B, authority/provenance closed by 008B2/008B4)

`POST /api/v1/loan-applications/{loan_application_id}/loan-documents/generate/` accepts exactly
`document_type`, `template_id`, and `output_format` (`pdf` or `docx`). It requires
`documents.loan_document.generate`, `documents.template.file_reference`, and canonical application
object access. The application must be sanction-approved and have one retained sanctioned decision.
The exact template id must be approved, effective today, match the requested type and the canonical
borrower variant, retain a non-null 008A2-referenceable source file, and retain local source bytes
whose size/checksum match metadata. Template read/manage and file upload/download do not imply
generation. Unresolved `fpc`/`producer_institution` variants fail configuration-required without
cross-variant fallback.

008B2 makes this legal-document module—not the HTTP view—the authoritative call boundary. Direct
task/test/orchestration callers and HTTP callers therefore receive the same permission, active-actor,
object-scope, state, template-reference, replay, and evidence decisions. Missing generation or
template-reference authority returns nondisclosing `403 FORBIDDEN`; an out-of-scope application
returns `403 OBJECT_ACCESS_DENIED`; all such denials occur before template/frozen-fact/file reads and
write no bytes, metadata, audit, or workflow rows. The unchanged v1 route is now transported by the
`legal_documents` app; the foundation `documents` app retains only file/template/storage ownership.

Declared merge fields are unique 008A facts and must appear in the retained template body as
`{{ field_name }}` placeholders. 008B supports the Term Sheet vocabulary recorded in A-100 plus
`witness_name`; every declared field must resolve from the approval-owned frozen review package and
sanctioned terms. Generation never rereads mutable nominee, witness, or shareholding rows. Unknown,
missing, or absent-placeholder facts return `400 VALIDATION_ERROR` field errors before generated
bytes, metadata, audit, or workflow evidence. Loan Agreement generation additionally returns
`409 INVALID_STATE_TRANSITION` until the same application has an executed Term Sheet.

Success uses the exact §26.4 object:

```json
{
  "loan_document_id": "uuid",
  "document_type": "term_sheet",
  "generation_status": "generated",
  "document_id": "uuid",
  "file_name": "term-sheet-LO00000801.pdf"
}
```

The generated file name contains only the normalized document type and application reference. The
retained generated file is confidential and the response grants no download. Exact
application/template/output-format replay returns the retained result with no additional file,
loan-document, audit, or workflow row. PostgreSQL application-row locking plus the database replay
constraint retains one winner under five concurrent identical requests. A real generation writes
one `documents.loan_document.generated` audit and one `loan_document_generation` workflow event
containing actor/request/template/version/type/format/file metadata only—never rendered content.
Storage/metadata failure removes generated bytes and rolls back every success row.

008B4 binds every new success to renderer contract `legal-renderer-v1`, the exact generated
`document_id`, and the SHA-256 recorded only after structural/content validation and storage. Exact
replay succeeds only while all three retained facts still match the current generated-file metadata.
A pre-provenance or mismatched retained row returns `409 CONFLICT` with
`renderer_validation_status=legacy_unverified` and a governed-successor remediation message; it is
never overwritten and creates no replacement bytes or evidence. This provenance proves renderer
output only—not execution, verification, stamping, notarisation, checklist completion, or A-101's
still-missing governed Term Sheet facts.

`GET /api/v1/loan-applications/{loan_application_id}/loan-documents/` requires
`documents.loan_document.read` plus the same object scope. It accepts only `page` and `page_size`
(defaults 1/20, capped at 100), applies application scope before count/pagination, and returns
metadata-only generated facts: the §26.4 fields plus category, required party, template id/version,
format, execution/verification/stamp/notary states, creation time, and
`renderer_validation_status` (`current_validated` or `legacy_unverified`). Legacy rows remain
visible for honest history but are excluded from current checklist-link selectors. It exposes no rendered merge
values, borrower facts, storage key, download descriptor, or mutation authority.

For both routes, a Compliance Team caller holding the route's permission receives standard
`404 NOT_FOUND` for an absent application. Missing-permission and unrelated-role callers receive
nondisclosing 403 first, before request validation or document queries.

008B2 moves eager loading, exact count, deterministic `-created_at/-loan_document_id` ordering,
bounded page normalization, and slicing into the legal-document selector after module-enforced actor
and application scope. The retained `loan_documents` table and rows have one Django owner in
`legal_documents`. Its nullable `loan_account_id` is database-constrained to `NULL` under A-102 until
009C can replace that transition with the source-required protected nullable FK.

## Stamp duty and notarisation records (008D/008D2)

`POST /api/v1/loan-documents/{loan_document_id}/stamp-duty-record/` requires
`documents.stamp.record`, an active Compliance Team or Company Secretary role, an approved Stage 4
application, and an 008B4 current-renderer-provenance loan document. It accepts exactly:

```json
{
  "stamp_paper_amount": "500.00",
  "stamp_type": "physical",
  "stamp_number": "MH-STAMP-123",
  "stamp_purchase_date": "2026-06-22",
  "executed_date": "2026-06-22",
  "status": "adequate",
  "remarks": "Verified by Company Secretary."
}
```

Amount is a required non-negative two-decimal string; type is `physical` or `electronic`; status is
`pending`, `adequate`, or `insufficient`; nullable dates use ISO `YYYY-MM-DD`, and purchase cannot
follow execution. Only Compliance Team authority may create or change `pending` preparation facts.
Both `adequate` and `insufficient` are Company Secretary verification outcomes; `adequate`
additionally requires an execution date. A checker outcome requires a retained pending preparation
by a different user. The platform persists the supplied amount and verification outcome but
performs no hard-coded ₹500 or ad-valorem adequacy calculation.

`POST /api/v1/loan-documents/{loan_document_id}/notarisation-record/` similarly requires
`documents.notary.record` and accepts exactly nullable notary name/registration/date, bounded
`pending`/`completed`/`rejected` status, nullable `evidence_document_id`, and nullable remarks.
Only Compliance Team authority may create or change `pending` preparation facts. Both `completed`
and `rejected` are Company Secretary verification outcomes, require a retained preparation by a
different user, and cannot be erased or replaced by a preparer; completed additionally requires
every notary identity, date, and evidence field. Non-null evidence must have one exact retained `documents.file.uploaded`
provenance ledger matching the current file metadata, `legal` category, and the same application.
The response returns evidence id/name metadata only and never grants download. The documents-owned
interface returns only generic immutable upload provenance. The legal-documents module owns legal
category, Stage-4 role, notary purpose, and same-application decisions.

Both routes cross one legal-documents-owned authority interface for action permission, sanctioned
Stage 4 queue scope, and current renderer provenance, then lock only the owning `LoanDocument`.
Request shape and simple decimal/date/UUID/enum parsing live at the legal HTTP serializer seam; raw
direct-module callers cross the same parser and business interface. Exact replay returns the current response with zero
writes; a changed POST updates the one-to-one current record and appends attributable audit,
version-history, and workflow evidence. The existing loan-document/checklist reads project only
current stamp/notary statuses. Current responses and every real history snapshot include nullable
`prepared_by_user_id` and `verified_by_user_id`; new checker outcomes require both and require them
to differ. Execution/verification states, renderer/template/file provenance,
checklist applicability/linkage/completion/verifier/remarks/signatures/status, and disbursement
readiness remain untouched. A changed status conflicting with completed checklist evidence returns
atomic `409 CONFLICT`; legacy/mismatched renderer provenance also returns zero-write `409 CONFLICT`.
Unknown/malformed fields return `400 VALIDATION_ERROR`; missing role/permission or non-Stage-4 scope
returns nondisclosing 403; an authorised missing loan-document id returns 404.

## Signature records and mismatch resolution (008E/008E2)

`POST /api/v1/loan-documents/{loan_document_id}/signatures/` requires
`documents.signature.record`, an active Compliance Team role, an approved Stage 4 application, and
an 008B4 current-renderer loan document. It accepts exactly the §26.7 fields:

```json
{
  "signer_party_type": "borrower",
  "signer_party_id": "uuid",
  "signer_name_snapshot": "Ramesh Patil",
  "signature_method": "wet_ink",
  "signature_status": "signed",
  "signed_at": "2026-06-22T10:30:00Z",
  "signature_mismatch_flag": false
}
```

Party type is `borrower`, `nominee`, `witness`, or `user`; method is `wet_ink`, `digital`, or
`scanned`; status is `pending`, `signed`, or `mismatch`. Pending carries neither signed time nor a
mismatch; signed requires a timezone-bearing signed time and forbids mismatch; mismatch requires a
true mismatch flag. New captures resolve borrower, selected nominee, application witness, or active
user identity through its canonical owner and reject null, arbitrary, wrong-party,
cross-application, or changed-name input. The canonical id/name and immutable Compliance capture
maker are frozen on first capture; nullable ids/makers remain legacy-schema history only. Exact
replay uses the frozen snapshot and is zero-write even if mutable display data later changes.
Pending/signed facts may progress normally, but an unresolved mismatch cannot be replaced or
cleared through capture, and a resolved row cannot be reopened.

`POST /api/v1/signature-records/{signature_record_id}/resolve-mismatch/` requires
`documents.signature.resolve_mismatch` and active Company Secretary authority. It accepts exactly:

```json
{
  "mismatch_resolution_type": "bank_verification_letter",
  "mismatch_resolution_document_id": "uuid",
  "remarks": "Signed and stamped bank verification received."
}
```

Resolution type is only `bank_verification_letter` or `borrower_declaration`. The evidence id must
be the retained file of an 008B4 current-renderer legal loan document of the corresponding type for
the same application. Borrower declaration additionally requires its exact 008D stamp-duty record
to be `adequate`; file existence or a cross-application/wrong-type/legacy reference is insufficient.
Only a current unresolved mismatch with a retained capture maker can be resolved, and the Company
Secretary resolver must be a different immutable user even after a role change. Exact replay
returns the retained §6.3 action response with zero writes; a different attempt to replace retained
resolution history returns `409 CONFLICT`:

```json
{
  "entity_type": "signature_record",
  "entity_id": "uuid",
  "previous_status": "mismatch",
  "new_status": "resolved",
  "workflow_event_id": "uuid",
  "available_actions": []
}
```

Both responses are metadata-only and expose no storage key/download action or file, checklist,
approval, or disbursement authority. Resolution evidence identity remains in the immutable
signature row/audit history rather than becoming download authority. Verified signature truth
crosses the application-owned fact interface through the single legal-owned application selector
and atomically changes only Bank Verification Letter applicability. Checklist status,
completion/verifier/time/remarks, display facts, approval signatures, and readiness stay unchanged;
a reversal against completed evidence returns zero-write `409 CONFLICT`. Missing action
permission/role returns 403 before owner queries. For an otherwise authorized resolver, unknown,
wrong-stage, unrelated, and non-current-renderer signature ids share the same nondisclosing 404
contract. Malformed fields return `400 VALIDATION_ERROR`; HTTP and direct module callers cross the
same typed legal serializer and business boundary.

## Security package and Power of Attorney (008F/008F2)

`GET /api/v1/loan-applications/{loan_application_id}/security-package/` requires
`security.package.read`; `POST .../security-package/refresh/` requires
`security.package.create` and accepts only an empty JSON object. GET permits active, explicitly
granted Credit Manager, Compliance, Company Secretary, scoped CFO/Director approvers, and persisted
audit-readonly actors against canonical latest-cycle frozen terminal sanction and matching Stage-4
checklist scope. Senior Manager Finance additionally requires the current checklist's
`sanction_approved` documentation truth (the pending-disbursement state). CFC remains denied until
Epic 009 supplies a canonical disbursement-ready relation; its role or permission alone is not
readiness. The same finance-state rule applies to package, PoA, SH-4, CDSL, blank-cheque, and
post-sanction checklist reads. Assigned approvers may read only their
case; an unrelated approver remains `403 OBJECT_ACCESS_DENIED`. Read authority returns masked
metadata only and never grants refresh, mutation, reveal, download, invocation, or release.
Refresh remains limited to active Compliance Team or Company Secretary actors. Mutable approved
status is insufficient. Refresh locks the application,
creates at most one package, and replays zero-write; unknown resources return 404 after authority,
while wrong-stage/stale-cycle resources remain nondisclosing. The narrow package is
always `pending`, returns `poa_required_flag=true` and `security_ready_flag=false`. Since 008J,
refresh sets both cheque flags true only when the application-owned selector proves one exact active
verified borrower bank account and its matching verified cancelled-cheque fact; missing, stale,
conflicting, or mismatched facts keep both false. Since 008H, refresh sets the SH-4/CDSL
applicability pair from
the canonical frozen sanction share mode: `physical` is `(true,false)`, `demat` is `(false,true)`,
and missing/`mixed` is `(false,false)` with the existing checklist blocker retained. It includes
metadata-only current PoA/SH-4 projections and never grants document download, invocation, release,
checklist completion, or disbursement readiness.

`POST/GET /api/v1/security-packages/{security_package_id}/power-of-attorney/` and
`PATCH /api/v1/power-of-attorneys/{power_of_attorney_id}/` implement §28.3. GET requires package-read
authority. POST/PATCH require `security.poa.manage`; only Compliance prepares/changes drafts and
material edits transfer current-maker identity. An active-role Company Secretary may activate only
as the retained attorney distinct from the current preparer. Requests contain borrower, nominee, attorney
user, retained purpose, PoA loan-document, stamp record, notary record, execution status,
effective-from date, and status fields. Status is only `draft`/`active`; execution is only
`pending`/`executed`. `invoked` and `released` are rejected with zero writes.

The borrower and nominee must be the sanctioned application's current retained parties. The
attorney must be an active Company Secretary. The retained purpose must explicitly authorise the
Company Secretary to initiate share sale on default; only a bounded negation of that authority is
rejected, so unrelated lawful negative clauses remain valid. Creation accepts only a pending draft tied to
the same application's current-renderer `power_of_attorney` document and that exact document's stamp
and notary rows. Activation additionally requires executed/effective facts, an adequate stamp
retaining exactly `₹500.00`, and completed notarisation rows with non-null distinct preparer/verifier identities, plus exactly one
current `signed` borrower row and one current `signed` selected-nominee row from the 008E2 legal
selector. Signature ids/names must match canonical frozen parties, mismatch/resolution facts must be
absent, signed time and capture maker must be retained, and A-108/A-109 legacy rows are ineligible.
Missing/null stamp references and adequate amounts below or above `₹500.00` fail atomically with
`400 VALIDATION_ERROR`; the generic stamp recorder and unresolved Loan Agreement duty rule do not
change.

Package/PoA/checklist rows are locked in one transaction. One current PoA is database-enforced per
package. Terminal activation replays the durable §6.3 action (`entity_type`, `entity_id`, prior/new
status, workflow id, no actions); changed activation, downgrade, `invoked`, and `released` write
nothing. It freezes renderer/file/checksum, stamp/notary/signature/PoA maker-checkers, and request
facts. The consumed legal document blocks later signature/stamp/notary changes atomically. Real
draft changes append audit/version/workflow evidence. Checklist projection changes only PoA metadata and
preserves item/package completion, verifier, remarks, approval signatures, status, file access, and
readiness. Projection conflict rolls back the PoA write and success evidence. Twice-run five-worker
PostgreSQL changed-activation and downgrade races retain one terminal activation ledger.

Pre-008F2 active PoAs retain `legacy_activation_evidence=true`, null workflow id, and no fabricated
snapshot under A-112. They are readable/terminal; PATCH replay conflicts because no action id exists.

## SH-4 physical-share security (008H)

`POST/GET /api/v1/security-packages/{security_package_id}/sh4-share-transfer-form/` and
`PATCH /api/v1/sh4-share-transfer-forms/{sh4_share_transfer_form_id}/` implement §28.4. The request
contains exactly `member_id`, `witness_id`, `shareholding_id`, nullable positive `share_count`,
`loan_document_id`, `form_status`, nullable bounded `custody_location`, and nullable ISO
`signed_at`. GET requires `security.package.read`; POST/PATCH require `security.sh4.manage` and the
same canonical latest-cycle Stage-4 package scope. Compliance creates/changes preparation facts;
only a distinct active Company Secretary records terminal custody. Other document, signature,
download, PoA, or security permissions imply no SH-4 mutation or file access.

Only frozen `physical` share mode is applicable. The member must be the sanctioned borrower; the
witness must be that application's verified existing-shareholder witness backed by active
shareholding; the selected shareholding must be the borrower's active physical row. `share_count`
cannot exceed its retained available shares and does not reserve/decrement them. The document must
be the same application's current-renderer `sh4` output. `signed`/`held_in_custody` require its exact
non-legacy borrower and witness signatures (canonical ids/names, signed time, capture makers, no
mismatch) and current adequate non-legacy maker/checker stamp evidence. No nominal amount is
hard-coded. The custody checker must differ from the retained SH-4 preparer and every current
material stamp/signature maker.

Statuses are only `pending`, `signed`, and `held_in_custody`; invocation/return fields remain
database-null and `invoked`/`returned` requests fail zero-write. One row per package is database
enforced under the package lock. Exact replay is zero-write; real preparation changes retain full
old/new audit/version/workflow facts. Terminal custody returns the retained §6.3 action identity and
freezes exact renderer/file/checksum, stamp, signature, maker, custodian, and request context.
Consumed signature/stamp evidence cannot later be changed. Checklist/security reads project only
existence, document/signature/custody metadata and preserve completion, verifier, remarks, approval
signatures, PoA/package state, file access, and readiness. Twice-run PostgreSQL five-worker create
and changed-custody races retain one current/terminal SH-4 and zero loser success evidence.

## CDSL demat-share pledge (008I)

`POST/GET /api/v1/security-packages/{security_package_id}/cdsl-share-pledge/` and
`PATCH /api/v1/cdsl-share-pledges/{cdsl_share_pledge_id}/` implement §28.5. The main request accepts
exactly pledgor member, the canonical SFPCL pledgee name, write-only 16-digit pledgor/pledgee BO
accounts, both DP names, `prepared`/`submitted` PRF status, nullable unique PSN, bounded
`pending`/`accepted`/`rejected` acceptance, nullable positive share count, nullable agreement
reference, bounded `pending`/`created` pledge status, and nullable evidence-document id. Invocation,
unpledge, and their timestamps are neither accepted nor persisted; 011I owns those actions.
Pending POST/PATCH may retain and return `evidence_document_id: null` and project a null checklist
loan-document link. Accepted/rejected terminal verification still requires the exact current
same-application evidence and returns `400 VALIDATION_ERROR` with no terminal write when it is null.

GET requires `security.package.read`. POST/PATCH require `security.cdsl_pledge.manage` and the same
canonical latest-cycle Stage-4 package scope. Only frozen `demat` mode is applicable; `physical`,
`mixed`, or missing mode cannot create a pledge. The pledgor must be the sanctioned borrower with
active demat shareholding, the pledged count cannot exceed retained available demat shares, and the
pledgee must be `Sahyadri Farmers Producer Company Limited`. The evidence id must be the retained
file of the same application's current-renderer `cdsl_pledge_evidence` legal document; reference
never grants download. The future-shares obligation is a non-client-editable,
database-constrained `true` fact under A-113.

Compliance creates/changes pending preparation. `submitted` requires a PSN, every real preparation
edit transfers current-maker attribution, and an exact replay is zero-write. A distinct active
Company Secretary may accept or reject only the exact retained submitted facts. Acceptance requires
both BO/DP facts, PSN, positive in-bounds count, loan-agreement reference, current evidence, and
`created` status; rejection remains uncreated. Accepted/rejected outcomes are terminal, return the
retained §6.3 action, and freeze masked BO values plus PSN/agreement/count/future-shares,
renderer/file/checksum, maker/checker, request/network/role/team facts. A role change cannot collapse
maker/checker identity, and database constraints enforce terminal evidence coherence.

Ordinary pledge, package, checklist, audit, version, and workflow responses show only last-four
masked BO values. `POST /api/v1/cdsl-share-pledges/{cdsl_share_pledge_id}/reveal-bo-accounts/`
accepts exactly `{ "reason": "..." }`, requires the dedicated
`security.cdsl_pledge.reveal` permission, package-read/object scope, and active Company Secretary
authority, and returns both full values with a five-minute expiry under A-114. Each permitted reveal
and denial is separately audited without plaintext. The response is `Cache-Control: no-store` and
`Pragma: no-cache`; one success per actor/pledge in that five-minute window is allowed, with repeated
requests returning `429 RATE_LIMITED` under A-116. BO sensitivity does not require re-authentication,
and that policy decision is retained in the central sensitive-access audit. New BO values use the
independently keyed/versioned AES-GCM `shared.encryption` convention in A-115. Since 008K2,
`field:v2` tokens contain only format/key identifiers, random nonce, and authenticated ciphertext;
field name and plaintext byte length are authenticated as associated data but no length or display
suffix is stored in cleartext. CDSL ordinary masking reads a separately retained, migration-
reconciled four-digit display projection; it never decrypts the ciphertext. Only the central,
reason-bearing reveal boundary decrypts. Field-specific lookup
hashes support equality/replay checks but are never returned. Retained `seal:v1` rows migrate with
row-count/hash/last-four reconciliation, and retained suffix-bearing `field:v1` CDSL/cheque rows
then migrate through a frozen decrypt/re-encrypt implementation with row-count/hash/plaintext-
absence reconciliation and no plaintext response or ledger exposure.

Package/checklist reads project only masked pledge existence, PRF/PSN/acceptance/created milestones,
share count, maker, checker, and current legal-document linkage. They preserve PoA/SH-4 facts,
completion/verifier/remarks/signatures, package status, file authority, share balances,
loan-account state, and `security_ready_flag=false`. Projection conflict rolls back the pledge and
all success evidence. Twice-run PostgreSQL five-worker different-PSN create and changed-acceptance
races retain one current row, one terminal winner ledger, replay-safe same-payload returns, unique
PSN integrity, masked history, and no loser success evidence.

## Blank-dated cheque and cancelled-cheque custody (008J)

`POST/GET /api/v1/security-packages/{security_package_id}/blank-dated-cheque/` and
`PATCH /api/v1/blank-dated-cheques/{blank_dated_cheque_id}/` implement §28.6. POST accepts exactly
`member_id`, `bank_account_id`, write-only six-digit `cheque_number`, nullable `document_id`,
`cheque_status`, nullable `custody_location`, and non-future ISO `collected_at`. PATCH accepts any
non-empty subset of those fields, merges it against the locked current row, and revalidates the
complete candidate. Omitted fields remain unchanged; explicit null is accepted only for
`document_id` and `custody_location`. Empty, unknown, and later-owner immutable shapes are rejected.
Status is only
`collected` or `held`; invocation approval, presentation date/amount, return date, `invoked`, and
`returned` are rejected and database-constrained to later owners.

GET requires `security.package.read`; mutation requires `security.blank_cheque.manage` and canonical
terminal-sanction/package scope. Active Compliance authority creates or changes collected facts. A
distinct active Company Secretary may record `held` only with a bounded custody location and the
exact retained Compliance member, bank, cancelled-cheque, cheque, scan, and collection-date facts.
Held custody is terminal here. One row per package and one field-specific cheque lookup hash are
database-enforced. Exact replay is zero-write; real changes append attributable audit/version/
workflow evidence, while held custody freezes maker, custodian, workflow, request/network, role,
and team facts.

The member must be the sanctioned borrower. The bank must be the exact application-retained active
verified member account linked to the exact single same-application verified cancelled cheque with
matching protected account hash, IFSC, and last-four metadata. Caller text, account numbers,
cross-member rows, missing/pending/rejected rows, multiple/conflicting rows, and stale ids cannot
establish authority. A scan requires one exact immutable `documents.file.uploaded` ledger matching
current file metadata, `legal` or `security` category, and the same application; reference grants no
download.

New numbers use `shared.encryption.FieldEncryption` AES-GCM and field-specific lookup HMAC.
Ordinary cheque, package, checklist, audit, version, and workflow data always returns fixed
`******`; no recoverable fragments or plaintext are logged. Reads also project canonical
cancelled-cheque id, masked bank, IFSC/branch, status, custody, maker, and custodian metadata while
preserving checklist completion/linkage/verifier/remarks/signatures, package status,
`security_ready_flag=false`, and null loan account.

Security mutation and checklist evidence use one shared recursive sensitive-key redaction policy.
This ordinary evidence policy preserves already-masked display values but cannot authorize reveal;
reveal success/denial remains a separate central sensitive-access ledger.

`POST /api/v1/blank-dated-cheques/{blank_dated_cheque_id}/reveal-cheque-number/` accepts exactly
`{ "reason": "..." }`. It requires `security.blank_cheque.reveal`, package-read/object scope, and
active Company Secretary authority. The central sensitive-access owner serialises reveal under the
retained cheque lock, returns the full value with a five-minute expiry and no-store/no-cache headers,
and permits one success per actor/cheque per five-minute window. Every success and denial is audited
without plaintext; tampered ciphertext or unavailable keys return `409 CONFLICT`, repeated success
returns `429 RATE_LIMITED`, and missing authority returns `403 SENSITIVE_FIELD_ACCESS_DENIED`.

Capture/custody never completes the checklist, mutates bank/cancelled-cheque truth, presents or
returns the cheque, creates a loan account, changes package status/readiness, or grants scan
download. Twice-run PostgreSQL five-worker changed-create and changed-custody races retain one
current row, one terminal custodian/workflow, exact winner request/actor evidence, and zero loser
success evidence.

## Final documentation checklist actions (008K)

The exact §27.3-§27.7 routes are now available:

- `POST /api/v1/checklist-items/{checklist_item_id}/complete/` accepts exactly
  `loan_document_id` and nullable `remarks` (maximum 4,000 characters).
- `POST /api/v1/document-checklists/{document_checklist_id}/approve-as-company-secretary/`,
  `/approve-as-credit-manager/`, `/approve-as-sanction-committee/`, and
  `/sign-disbursement-complete/` each accept exactly one non-empty `comments` value (maximum
  4,000 characters).

Successful completion and the first three approvals return the durable §6.3 action shape plus
`checklist_action_id`. Exact same-actor/same-fact replay returns that identity without writes;
changed repeats return `409 CHECKLIST_ACTION_CONFLICT`. Wrong approval order returns
`409 CHECKLIST_APPROVAL_OUT_OF_ORDER`, incomplete terminal evidence returns
`409 CHECKLIST_EVIDENCE_INCOMPLETE`, and unrelated objects remain nondisclosing.

Completion accepts only the latest current-renderer same-application document of the canonical
item type and consumes owner-held terminal legal/security evidence. Masked CDSL/cheque ledgers are
never revealed or decrypted. CS approval requires every applicable required item complete; Credit
Manager approval requires the canonical frozen limit package; one active non-excluded director from
the frozen committee may give the final documentation approval. The Senior Manager Finance route
consumes the singular current successful-transfer decision through the top-level post-disbursement
evidence coordinator. An active Senior Manager Finance actor needs the explicit signature grant and
exact Stage-5 initiating-maker scope. The first valid request creates one immutable checklist
action/audit/workflow/version chain bound to the transfer, Loan Register update, pending advice
identity, evidence digest, and owner ids. Exact actor/comment replay is zero-write; changed actor/
comment, pre-success, missing or stale register/advice/transfer evidence, and cross-object scope fail
without changing finance or documentation truth. No route creates a loan account or changes
package/security readiness.

008K3 hardening: the completion route now receives security facts only through the public
cross-owner process coordinator and resolves current source-owned rows rather than accepting
`VersionHistory` JSON as truth. Cheque evidence must reconcile the exact application, package,
member, bank account, cancelled cheque/file, blank cheque/scan, maker, custodian, and custody
workflow while retaining only the fixed `******` mask. PoA, SH-4, and CDSL likewise reconcile their
current terminal owner rows; PoA requires an exact ₹500 adequate stamp. Term Sheet completion
requires borrower/nominee/frozen CFO signatures and, above ₹5,00,000, two eligible frozen-director
signatures. Company Secretary approval now revalidates every current item and requires exactly one
matching public completion action/history identity, current renderer checksum, verifier/time/
remarks, applicability flags/cycle, and terminal-evidence digest. Status-only, missing/extra,
stale, cross-object, or changed evidence returns `409 CHECKLIST_EVIDENCE_INCOMPLETE` with zero
approval writes. Retained actions freeze the role that authorised the requested stage, even for a
 multi-role user.

008K4 current-evidence and read closure adds:

- `POST /api/v1/loan-applications/{loan_application_id}/bank-verification-decision/`

The request requires `X-Request-ID` and exactly `bank_account_id`, `cancelled_cheque_id`, and
`decision_status` (`verified` or `rejected`). Authority is the existing Stage-4 checklist-update
permission held by Compliance Team or Company Secretary; no new verifier role is introduced. A
success binds the exact application/member/bank/cancelled-cheque file and checksum, verifier role
and time, request, workflow, audit, version, and evidence digest. Status-only legacy bank rows are
readable but cannot complete a new checklist item. Changed bank/file/ledger facts make the decision
non-current and return the existing `409 CHECKLIST_EVIDENCE_INCOMPLETE` at completion/approval.

Checklist completion, borrower-safe projection, and Company Secretary reconciliation now rerun the
current renderer, signature, stamp/notary, security, bank-decision, applicability/case, action,
workflow, audit, single-version, request, and digest checks through the top-level coordinator. Loan
document generation shares the application-first lock order and refuses a new generation after a
terminal item or checklist approval has consumed that boundary, so concurrent generation and
completion/approval retain one coherent winner.

Ordinary package, PoA, SH-4, CDSL, blank-cheque, and checklist GET projections expose only
source-documented business state and governed masks. They omit retained evidence blobs, maker/
checker ids, request/network context, role/team lists, signer snapshots, internal legal/audit/action
ids, hashes, ciphertext, and storage keys. Internal terminal selectors retain exact evidence without
granting it to readers. Canonical recursive redaction preserves only full fixed masks or a governed
last-four mask; mixed plaintext such as `1234*5678` is replaced with `[REDACTED]`.

008K5 authority closure: the bank-decision endpoint now resolves authority before any bank,
cheque, or document evidence and accepts writes only while the canonical application status is
`approved_by_sanction_committee`. Missing and every non-documentation state are zero-write scope
denials; unrelated or changed source identities remain zero-write conflicts. Success and exact
replay return the complete §6.3 action body (`entity_type`, `entity_id`, `previous_status`,
`new_status`, `workflow_event_id`, and `available_actions`) alongside the immutable decision and
source identities. Borrower-safe completion now requires singular exact workflow/audit/version
rows, their action linkages and full retained body, the current renderer/terminal body, and its
digest; any missing, extra, changed, cross-object, or newer source fact removes completion without
exposing the evidence.

008L5 current-terminal closure: `approved_by_sanction_committee` remains necessary but no longer
supplies sanction authority by itself. Under the application lock, every new or replayed bank
decision must resolve the approval owner's latest approved case and its sanctioned decision; the
response and immutable audit/version digest now include `approval_case_id` and
`sanction_decision_id`. Missing, rejected, returned, replaced, malformed, or stale latest-cycle
facts return nondisclosing `403 FORBIDDEN` before bank/document lookup or any decision/audit/
workflow/version write. Downstream cancelled-cheque/checklist truth also re-resolves those exact
retained ids and fails closed when they are no longer the current terminal cycle.

## Staff documentation workspace (008M)

- `GET /api/v1/documentation-workspaces/` returns the strictly paginated S26 queue; `GET /api/v1/loan-applications/{loan_application_id}/documentation-workspace/` returns one locked, redacted S26-S35 snapshot whose executable owner-authorized actions use the shared §44 shape and whose timeline omits internal evidence identities.
- `GET /api/v1/loan-applications/{loan_application_id}/documentation-workspace/{item_code}/download/` issues an actor/application/item/current-renderer-bound capability; content re-resolves current truth, records the generic staff download audit, and returns `404` after replacement/tamper.
- 008M3 replaces caller-controlled `fixed_payload` with `action_id` plus a stable unique `action_key`. Every mutation posts only its declared user fields to `POST /api/v1/loan-applications/{loan_application_id}/documentation-workspace/actions/{action_id}/`; the server re-resolves the locked actor/application/snapshot and all canonical object identities before calling the existing legal, checklist, security, bank, document-upload, or workflow owner.
- 008M5 makes `upload_signed_copy`, `request_correction`, `return_for_correction`, and
  `add_condition` durable legal-owner actions. A signed-copy success returns `signed_copy_id` and
  subsequent GETs project redacted `document.signed_copy {signed_copy_id, file_name, uploaded_at,
  remarks}` while retaining the generated original as the independent download source. Each
  successor preserves its predecessor; a corrected successor resolves the exact open item/return
  action. Open corrections project `status: blocked` plus `blocker: correction_requested`, appear
  in the pack/blocker/timeline surfaces, and deny item completion or checklist approval until the
  successor is retained. Conditions remain visible in `approval_stages[].conditions` at their exact
  approval role without becoming generic workflow state. The queue returns nullable `poa_blocker`
  beside `poa_status`. Exact replay of a retained opaque action identity returns the same owner row
  and workflow identity with zero writes; changed facts conflict, while actor/application/document/
  action-identity tamper is rejected without creating a file or legal ledger.
- 008M6 makes correction resolution a current-evidence decision rather than a reverse-relation
  check. A resolving upload must be the coherent successor of an existing current signed copy and
  must retain matching file/checksum, uploader, remarks, request/action, resolution-target,
  upload-audit, legal-audit, workflow, and version facts; missing, changed, duplicate, cross-target,
  stale-renderer, or ambiguous evidence keeps the correction blocked. A first signed upload with no
  predecessor remains an ordinary unresolved copy; only its coherent successor may resolve the
  correction. Review actions similarly require singular matching owner ledgers. Opaque
  `request_correction`, `return_for_correction`, and `add_condition` commands freeze the current
  approval stage and the effective primary or governed role that authorises that stage; changed
  stage evidence is neither projected nor accepted as approval truth.
- When PoA is required but the governed application-scoped attorney decision is absent, the security
  workflow returns `status: blocked`, `blocker: governed_attorney_unconfigured`, and no create
  action. A configured decision is accepted only from the security-owner seam when its application,
  attorney, and decision identities are all current; stale decisions return
  `governed_attorney_decision_stale`. Neither blocker grants attorney authority.
- The command boundary accepts JSON for ordinary actions and multipart `file` plus `remarks` for signed-copy upload/re-upload. Unknown, stale, tampered, cross-user, cross-application, or no-longer-advertised action identities return nondisclosing `404` with zero writes; field validation returns `400`, owner conflicts return `409`, success returns the owner's §6.3 action data, and the client refetches the workspace once.

## Member portal documentation actions (008L)

Authenticated borrower portal sessions use these application-scoped routes:

- `GET /api/v1/portal/applications/{loan_application_id}/documentation-actions/`
- `POST /api/v1/portal/applications/{loan_application_id}/documentation-actions/{action_code}/upload/`
- `GET /api/v1/portal/applications/{loan_application_id}/documentation-actions/{action_code}/download/`

Scope is derived only from the active `PortalAccount.member_id`. Missing applications, another
member's application, and internal-user tokens are nondisclosing `404 NOT_FOUND`; an inactive or
expired portal session is rejected by shared authentication. GET returns the application id,
reference, status, availability/blocker, and checklist-ordered borrower-safe actions: stable
checklist action code, label/section, required/applicable flags, reconciled status, updated date,
instruction/note, upload/re-upload flags, and nullable safe download metadata. It never returns
checklist/security ids, evidence identities, makers/checkers, comments, storage keys, BO/bank/cheque
values or fragments, ciphertext/hashes, workflow/version JSON, or internal action URLs. A complete
label requires the current checklist item, its exact completion action, and its one matching durable
completion history/evidence digest; status-only or stale/ambiguous evidence is shown pending.

Upload is `multipart/form-data` with exactly one non-empty `file` and optional trimmed `notes`
(maximum 4,000 characters). Under A-119 the file must be matching PDF/JPEG/PNG MIME plus extension
and at most 5 MiB. Accepted action codes are `cancelled_cheque`, `poa`,
`tri_party_agreement`, `sh4`, `term_sheet`, `loan_agreement`, and
`bank_verification_letter`, only while the current canonical checklist advertises that applicable
pending borrower action. CDSL and blank cheque are status/instruction only. Every accepted upload
creates a new central `DocumentFile`, immutable upload provenance, and append-only portal submission
successor row attributed to the portal account/member/application/action; the response contains only
safe file metadata. Re-upload retains every prior row. Upload never writes checklist completion,
signature, stamp/notary, security terminal/custody, bank verification, package/readiness,
loan-account, or disbursement facts. Unknown fields/action codes, crafted evidence fields, stale or
inapplicable actions, empty/oversize/type-mismatched files, and cross-member references fail before
any success evidence.

Only canonical latest current renderer-validated `term_sheet` and `loan_agreement` outputs receive a safe
download action. It returns a short-lived portal-scoped content URL; authenticated retrieval verifies
the retained bytes and writes exactly one central `portal.document.downloaded` event with portal
account, member, application, action, document/version/category/sensitivity, reason,
request/network, capability verification, and accepted outcome—never a checksum or storage fact.

008L4 closure: projection, upload, and download now consume one application/checklist-locked
action-authority decision, including locked current submissions and canonical latest generated
renderer outputs. A pending
required/applicable item is mutable only when it has no applicability blocker and no retained
completion status; a stale/status-only completion remains honestly non-complete but advertises
neither upload flag and cannot be reopened by a crafted POST. Accepted upload/re-upload uses only
the central `portal.document.uploaded` vocabulary with portal attribution and immutable version/
predecessor facts, without a parallel generic event. Downloads use the central signed capability:
the content URL contains a token,
not caller-editable expiry authority, and the signature binds portal account, member, application,
action, current loan document, and current file. Tamper, expiry, replacement, cross-action, and
cross-scope reads are nondisclosing and write no success event. Responses remain `no-store` at the
HTTP content boundary. A production generation successor immediately changes projection/download
authority and invalidates a descriptor issued for its predecessor; no checklist pointer assignment
participates in current-document selection.

## Member portal deficiency response and resubmission (008L2)

Authenticated active borrower sessions use only the `PortalAccount.member_id` scope:

- `GET /api/v1/portal/applications/{loan_application_id}/deficiencies/`
- `POST /api/v1/portal/applications/{loan_application_id}/deficiencies/{deficiency_id}/upload/`
- `GET /api/v1/portal/applications/{loan_application_id}/deficiencies/{deficiency_id}/download/`
- `POST /api/v1/portal/applications/{loan_application_id}/deficiencies/resubmit/`

GET returns the canonical application status, whether resubmission is currently allowed, and open
deficiencies with borrower-facing description, current response, and a server-owned upload contract
(category, sensitivity, extensions, and 5 MiB limit). Staff remarks, raiser/resolver identity,
storage keys, protected member data, and internal completeness actions are omitted. Cross-member
reads/actions are nondisclosing `404 NOT_FOUND` and write a denied portal audit; staff tokens are
`403 FORBIDDEN`, while expired/suspended portal sessions remain shared `401` errors.

Upload is strict `multipart/form-data`: one non-empty PDF/JPG/JPEG/PNG whose extension matches MIME,
at most 5 MiB, required server-advertised `document_category` (`kyc`, `legal`, or `finance`) and
`sensitivity_level` (`confidential`), plus optional trimmed `response_remark` up to 4,000 characters.
Every accepted upload creates a central `DocumentFile`, the next pending `ApplicationDocument`
version for staff verification, and an immutable deficiency-owned successor row attributed to the
exact portal account/member/application/deficiency. Re-upload retains history; only the current
successor is projected. Content download returns a short-lived portal-scoped URL,
requires a second authenticated request, verifies checksum/size, and audits the accepted read.

Resubmit accepts an empty JSON object and atomically requires a current response document for every
open deficiency. It retains those deficiency rows as open for staff verification/resolution under
the existing 005F permission, resets completeness to `not_started`, and moves canonical application
status from `incomplete_returned` to `submitted`, reopening the existing staff completeness queue.
008L3 places that transition behind the application-owned `resubmit` transition guard and canonical
`applications.loan_application.resubmitted` audit/workflow writer. Upload/re-upload and resubmit
workflow facts target the immutable deficiency-response aggregate (`absent/responded -> responded ->
submitted_for_review`); they never claim that the staff-owned open deficiency changed state. The
008L4 borrower projection derives the current immutable response state from those retained workflow
facts, so it reports `submitted_for_review` after resubmission while the staff-owned deficiency
continues to report `open`. Deficiency uploads and downloads likewise retain exactly one central
`portal.document.uploaded` or `portal.document.downloaded` event with safe portal scope and document
metadata, without a parallel generic event or checksum/storage disclosure. The
borrower timeline shows `Application resubmitted` (A-129). Empty, partially responded, or
non-returned applications fail before any transition. Deficiency actions never create or change
Stage-4 checklist items/actions/history, approvals, verifier/role/remarks, legal/security evidence,
readiness, loan-account, or disbursement truth.

008L5 response-evidence closure: each projected current response is `responded` only when it has
one exact borrower-attributed `absent/responded -> responded` workflow fact, and becomes
`submitted_for_review` only when that fact is followed by one exact
`responded -> submitted_for_review` fact. Missing, duplicate, wrong-workflow/entity/actor/state,
reversed, contradictory, or extra terminal facts project `response_status = evidence_invalid`,
set `resubmission_allowed = false`, and make resubmit return `400 VALIDATION_ERROR`. The open staff
deficiency remains unchanged and internal workflow evidence ids are never returned.

## SAP customer profile request (009A)

- `POST /api/v1/loan-applications/{loan_application_id}/sap-customer-profile-request/`

The authenticated actor must be an active persisted Credit Manager with
`finance.sap_request.create` and canonical application object access. The JSON request accepts
exactly `assigned_to_user_id`, which must resolve to one active persisted Senior Manager Finance
user. Borrower, application, sanction, and optional current verified-bank facts are server-derived;
unknown client fields return `400 VALIDATION_ERROR`.

Creation requires the application owner's latest approval case to be approved and its exact
`SanctionDecision` to be `sanctioned` with a positive amount/date. It locks that evidence and the
member before freezing name/type, folio, full registered address, optional contacts, application
number, sanction facts, encrypted PAN, individual-only encrypted Aadhaar, and current verified bank
last-four/IFSC when available. An active member SAP code returns `409 CONFLICT`; a
missing/current-state failure returns stable validation, `INVALID_STATE_TRANSITION`, `FORBIDDEN`, or
`OBJECT_ACCESS_DENIED` envelopes without creating a row/file/event.

Success returns only `sap_customer_profile_request_id`, `request_status: draft`, `excel_file_id`,
and canonical `assigned_to_user {user_id, full_name}`. The linked file is a checksum-retained,
restricted genuine `.xlsx` Annexure I whose physical storage bytes are authenticated ciphertext;
The SAP owner's Annexure storage boundary verifies, decrypts, and returns the readable workbook. The
response and audit/workflow evidence omit PAN, Aadhaar, address, and bank secrets. The active-request
identity is application plus status `draft`/`sent`: sequential or concurrent retry returns the
retained projection and creates no duplicate file, audit, or workflow event, unless an active
member SAP code now exists, in which case a new request may be retained for explicit governed reuse.
Correction, loan-account, readiness, and disbursement changes are not part of this route.

## SAP request delivery, completion, reuse, and masked read (009B/009B2)

- `POST /api/v1/sap-customer-profile-requests/{request_id}/send/` accepts exactly optional string
  `remarks`. The active persisted Credit Manager with `finance.sap_request.send` must be the frozen
  requester. The application/member/current sanction cycle, active frozen Senior Manager Finance
  assignee, request row, and active member code are locked before the restricted Annexure-I is
  checksum-verified and decrypted. The public `sap_workflow.modules.sap_customer_profile` owner
  sends those exact plaintext workbook bytes through the manual `SapAdapter`; the adapter makes no
  real email/SAP call and must return one accepted delivery reference and the same plaintext SHA-256
  before the request can become `sent`. Success returns request id, status/time, assignee,
  `communication_id`, in-app `task_id`, and `delivery {delivery_reference, checksum_sha256,
  document_id, capability_path}`. The task body contains no file id or capability. Exact sent replay
  returns the retained delivery identity with no writes; changed remarks, workbook/checksum/file,
  assignee, completed/stale requests, wrong owner/role/object, invalid retained files, or adapter
  rejection conflict without another success artifact.
- `POST /api/v1/sap-customer-profile-requests/{request_id}/annexure-i-delivery-capability/` accepts
  exactly `{}` and is restricted to the frozen active Senior Manager Finance assignee holding
  `finance.sap_request.complete`. It issues or replaces one signed 15-minute, assignee/request/file/
  delivery/checksum/version-bound capability. Success returns only delivery reference, plaintext
  checksum, capability, and expiry; replacement invalidates the previous capability.
- `GET /api/v1/sap-customer-profile-requests/{request_id}/annexure-i/?capability=...` accepts exactly
  one capability query parameter. A current unconsumed capability returns the checksum-verified,
  decrypted retained `.xlsx` bytes with attachment and `nosniff` headers, atomically consumes the
  capability, and creates exactly one safe `sap.annexure_i_downloaded` audit. Expired, replaced,
  tampered, consumed, cross-user, cross-request/application/file, or incoherent delivery attempts
  fail nondisclosingly and retain a safe denial audit; tokens and workbook/identity/bank plaintext
  never enter audit, communication, workflow, or response metadata.
- `POST /api/v1/sap-customer-profile-requests/{request_id}/complete/` accepts exactly required
  `sap_customer_code` plus optional `sap_vendor_code`, `created_at_sap`,
  `confirmation_document_id`, and `confirmation_notes`. Codes and notes are trimmed; codes are
  canonical uppercase, nonblank, and at most 120 characters. SAP timestamps must be timezone-aware
  and not future. Only the active persisted frozen Senior Manager Finance assignee with
  `finance.sap_request.complete` may complete the exact current sent request.
- Completion creates one globally case/padding-insensitive unique active member code or reuses that
  member's retained active code. It never infers reuse from identity text, reactivates inactive
  history, overwrites retained code evidence, or accepts another member's code. A request pending
  before another request completed for that member loses with `409`; a later request may explicitly
  reuse the retained code. The first accepted request freezes a canonical digest containing each
  field's supplied-versus-omitted marker plus its normalized value. Replay is HTTP 200 only when all
  five canonical fields match that digest; adding, omitting, or changing any retained optional value
  returns `409 CONFLICT` with no success artifacts.
- Optional confirmation evidence must have one immutable upload-provenance row, sensitivity
  `restricted`, category `sap_confirmation`, uploader equal to the assignee, and scope equal to the
  request or its loan application. Missing, cross-object, public, template/portal, other-uploader,
  or ambiguous evidence returns the same nondisclosing field error.
- Completion returns request/code/member/application ids, `completed`, completion time, `reuse`,
  masked customer/vendor codes, and safe confirmation-file metadata. It never returns frozen
  identity/bank values, storage keys, signed capabilities, or raw code values. It creates one safe
  audit and workflow ledger only: new confirmation uses mandatory `sap.customer_code_created`, reuse
  uses `sap.customer_code_reused`, and both freeze actor role/team/request/network context without
  raw codes. It creates no loan account, readiness, payment, disbursement, or borrower communication
  truth.
- `GET /api/v1/members/{member_id}/sap-customer-code/` requires an active persisted Senior Manager
  Finance user with `finance.sap_code.read` who is the assignee on a completed request bound to the
  member's current active code. Success returns only code id, member id, masked customer/vendor code,
  and active status. Missing and out-of-scope member identifiers share `403 OBJECT_ACCESS_DENIED`
  and the response never exposes SAP request or borrower identity fields.

Trusted downstream modules use `SapCustomerProfileModule.get_customer_code_for_member(member_id)`.
It returns an immutable coherent decision containing only customer-code, member, completed-profile-
request, and loan-application ids plus active status, or `None`. Consumers must not import Finance
SAP models, adapter internals, retained workbook storage, or SAP exception vocabulary.

009B3B keeps these route paths, HTTP statuses, success fields, field errors, idempotency identities,
audit/workflow vocabulary, ciphertext context, and nondisclosure rules unchanged while aligning
touched workflow errors with §7: stale/invalid states use `409 INVALID_STATE_TRANSITION`; changed
replays, duplicate-code conflicts, rejected adapter results, and invalid/expired delivery
capabilities use `409 CONFLICT`. Executable request, rendering/storage, send, capability/download,
completion/reuse/read, and Manual/Fake/Future adapter policy now live under `sap_workflow` and import
no Finance model or implementation. `finance.models` remains only the object-identical legacy model
import established by 009B3A; the former Finance SAP orchestration modules no longer exist.

## Loan account creation from terminal sanction (009C)

- `POST /api/v1/loan-applications/{loan_application_id}/create-loan-account/` accepts a JSON object
  containing exactly required `sanction_decision_id` (UUID) and `loan_account_number`. The account
  number is trimmed, internal whitespace is collapsed, and the retained value is limited to 80
  characters. Global uniqueness uses the collapsed case-folded form, so case/whitespace-equivalent
  identifiers conflict.
- The actor must be an active persisted user with the Critical
  `finance.loan_account.create` permission and canonical application object scope. The permission
  remains in the catalogue with no production role grant (A-121); missing permission returns
  `403 FORBIDDEN`, while missing or inaccessible parents return nondisclosing
  `403 OBJECT_ACCESS_DENIED`.
- Creation locks the application/member/current nominee/shareholding, latest approval case, supplied
  sanction decision, current executed/verified renderer-valid Term Sheet and Loan Agreement, and
  the SAP owner's public active-code decision. The application must remain terminal-approved and
  the supplied decision must be the latest approved case's positive `sanctioned` decision. Frozen
  review identities must still match the current safe borrower, nominee, and active-shareholding
  facts. Missing governed purpose, amount/date, loan type, rate, tenure, repayment, penalty,
  charges, security, dispute, or current legal evidence returns field-specific
  `400 VALIDATION_ERROR`; replaced/non-terminal source truth returns `409 STALE_STATE`.
- A coherent SAP decision links only when its active code, member, and originating application all
  match. `None`, inactive, or mismatched decisions retain a nullable link; creation never reads raw
  code values, Annexure-I delivery/capability facts, adapter state, or Finance exception details.
- Success atomically creates one `sanctioned` account, one immutable terms package, one append-only
  null-to-sanctioned history row, one safe `finance.loan_account.created` audit, and one
  `LoanAccountCreated` workflow event. `disbursed_amount` and every outstanding balance are zero;
  no readiness, schedule, payment, activation, register, communication, or borrower-visible truth
  is created. The response contains only account/application/member/sanction ids, nullable SAP-code
  id, canonical account number/status, amount/type/rate/repayment projection, and terms id.
- Exact application + sanction id + normalized account-number retry returns the retained projection
  with no ledger writes. A changed retry or globally duplicate normalized number returns
  `409 LOAN_ACCOUNT_CONFLICT`. Database uniqueness and transaction locks retain one complete tuple
  under concurrent first create; integrity losers receive the same conflict without partial terms,
  status, audit, or workflow evidence.

## Disbursement readiness (009D)

- `GET /api/v1/loan-accounts/{loan_account_id}/disbursement-readiness/` accepts no query
  parameters. Unknown parameters return `400 VALIDATION_ERROR`. The actor must be active and
  persisted, hold `finance.disbursement.readiness`, have canonical loan-account/application object
  scope, and have at least one active effective Senior Manager Finance, Chief Financial Controller,
  Credit Manager, CFO, or explicitly audit-scoped Internal Auditor role. Effective roles include a
  valid active governed `approval_authority_type`; the canonical scopes of all effective roles are
  unioned. Senior Finance is limited to the newest SAP assignment, CFC to an exact pending initiated
  disbursement, Credit to active/monitoring loan states, CFO to portfolio detail, and Auditor to its
  active read-only grant. Missing and inaccessible ids share `403 OBJECT_ACCESS_DENIED`; an unknown
  or inactive authority, role alone, permission alone, or intake assignment is insufficient.
- Success returns `loan_account_id`, `loan_application_id`, `ready_for_disbursement`, UTC
  `evaluated_at`, and all ordered checks. Each check contains only stable `code`, `label`, `status`
  (`pass`/`fail`), plus a safe `reason` only when failed. The fixed order is sanction, sanctioned
  account state, conditional exception/general-meeting approvals, KYC, appraisal, checklist,
  Company Secretary/Credit Manager/Sanction Committee approvals, security package, PoA, Term Sheet,
  Loan Agreement, explicit SH-4 and CDSL paths, blank cheque, cancelled cheque, borrower bank,
  signature resolution, SAP code, source bank, and amount within sanction.
- The loan owner locks the exact account/application/member/terms source and enforces authority.
  Approval, legal/checklist, security, application-bank, SAP, and configuration owners return their
  own bounded immutable decisions inside the same transaction. Missing, stale, replaced,
  cross-object, inactive, non-terminal, or mixed relationships fail their named checks; no check is
  omitted. The SAP check compares the account link only to
  `SapCustomerProfileModule.get_customer_code_for_member(member_id)` and never reads raw/masked
  codes, Annexure-I, adapter, delivery, or Finance model state. Signature resolution considers only
  the latest current applicable Term Sheet, Loan Agreement, PoA, tri-party agreement, and SH-4;
  unrelated signature history is ignored, while missing, extra, wrong, duplicate, or unresolved
  current required signers fail closed against the approval-owned Term Sheet signer set.
- `ready_for_disbursement` is true only when every check passes. Senior Manager Finance final
  verification/initiation and CFC authorisation are later actions and are not readiness checks.
  Under A-126 the source-bank check fails honestly until a governed owner exists. Evaluation writes
  no audit, workflow, checklist, approval, security, account, balance, payment, task, communication,
  register, or borrower truth and exposes no identity/bank/document/cheque/BO/capability secrets.

## Borrower portal disbursement status and advice (009I)

- `GET /api/v1/portal/applications/{loan_application_id}/disbursement-status/` accepts no query
  parameters and writes no audit or workflow evidence. An active borrower portal session may read
  only the application owned by its canonical `PortalAccount.member_id`; missing and cross-member
  ids share `404 NOT_FOUND`, staff sessions receive `403 FORBIDDEN`, and invalidated portal sessions
  retain the shared `401` contract.
- The response contains only application/account ids, one borrower-safe status code/label, decimal
  sanctioned and nullable disbursement amounts, destination and bank-reference last four, UTC
  disbursement time, advice availability, and the fixed ordered documentation/SAP/initiation/CFC/
  transfer/advice timeline. It composes current sanction, disbursement, transfer, and finalized
  communication owner decisions. Missing or incoherent terminal evidence cannot imply success;
  internal actors, comments, raw SAP/bank values, evidence ids, and communication internals are
  never returned. Documentation and SAP stages compose the current legal-readiness and member-level
  SAP customer-code owner decisions; a legitimately reused active SAP code is current when the loan
  account binds that exact code identity. Every stage uses its retained owner timestamp or null.
- `POST /api/v1/portal/applications/{loan_application_id}/disbursement-advice/download-capability/`
  accepts exactly an empty JSON object. For the exact current finalized advice it replaces any
  earlier capability and returns only `download_url` and UTC `expires_at`. The signed 15-minute
  capability binds portal account, member, application, loan account, advice intent,
  communication-owned artifact/checksum, and version. Internal capability and audit claims name
  that identity `artifact_id`; they do not describe a delivery outbox as a governed file.
- `GET /api/v1/portal/applications/{loan_application_id}/disbursement-advice/content/?capability=...`
  accepts only that query parameter. It re-resolves current owner truth, expires and consumes the
  capability once, and returns the retained UTF-8 borrower advice as an attachment with
  `Cache-Control: no-store` and `X-Content-Type-Options: nosniff`. Replacement, replay, expiry,
  tamper, cross-scope, and changed evidence share nondisclosing `404 NOT_FOUND`.
- Capability issuance and accepted/denied content attempts use `portal.document.downloaded` with
  safe identity, request/network context, and `issued`/`accepted`/`denied` outcomes. Audit payloads
  never retain the capability, advice bytes, recipient, full UTR/account/SAP values, storage keys,
  or internal authorisation facts.

## Loan Account 360 initial reads (009J)

- `GET /api/v1/loan-accounts/?page=1&page_size=20` returns the standard strict pagination envelope.
  `page`, `page_size`, `search`, `loan_account_status`, and `member_id` are supported; page values
  are positive and `page_size` is at most 100. `dpd_bucket` is recognized but returns an explicit
  Epic 010 deferral until the DPD owner exists; other parameters remain unknown.
  and an out-of-range page returns `400 VALIDATION_ERROR`. Results are deterministically ordered by
  newest account creation and UUID. Scope is applied before pagination and incoherent accounts are
  excluded rather than projected from mutable labels.
- `GET /api/v1/loan-accounts/{loan_account_id}/` returns the same item projection as the list.
  Missing, out-of-scope, and evidence-incoherent identifiers share `404 NOT_FOUND`; neither route
  reveals whether a denied account exists. Missing authentication retains the shared `401` contract,
  while an active actor lacking either the effective source role or `finance.loan_account.read`
  receives `403 FORBIDDEN`.
- Both reads require an active persisted effective role and permission plus the canonical account
  scope. Accounts Head and explicitly granted CFO roles receive portfolio scope; Credit Manager is
  limited to active/monitoring statuses; Senior Manager Finance uses the current SAP assignment;
  CFC uses exact current initiation or post-transfer evidence; Company Secretary uses the terminal
  sanctioned-documentation parent; Internal Auditor additionally requires its active audit-read
  grant. Intake assignment, raw ids, permission alone, and role alone grant nothing.
- `finance.disbursement.initiate` never substitutes for `finance.loan_account.read`. The staff
  workspace composes its initiation rows through a distinct mutation-candidate owner, so an actor
  can receive an initiation action without gaining the public list/detail contract or portfolio
  scope. Public list and detail retain identical role, permission, and exact-object decisions.
- Each item contains only account/application ids and display references, member id/display name,
  safe SAP customer code or null, loan/facility/rate types, exact decimal amount/balance strings,
  stable `sanctioned`/`active` status, tenure/repayment dates and months, and UTC creation/activation
  timestamps. A sanctioned account must have zero funding and balances with no activation date. An
  active account must reconcile the immutable 009C creation ledger and exact singular 009G3
  transfer, activation history, register, advice-intent, and amount/balance evidence.
- Full bank/UTR values, destination/source accounts, evidence/checksum/storage ids, internal actors,
  comments, request/network/idempotency facts, member identity/contact values, register identities,
  and advice/provider identities are never returned. Both reads are transactionally zero-write and
  create no audit or workflow event.
- 009L5 makes the collection identity set owner-composed and exact: lifecycle creation, the latest canonical
  SAP member/application/code decision, and post-transfer evidence are filtered before count and
  database pagination. Count, offsets, total pages, and projection consume the same requested
  database identity window; evidence-incoherent rows cannot inflate totals or shift page reachability,
  and query count remains independent of portfolio size.
- 009L6 binds each lifecycle audit body to its retained owner selector manifest. The database
  selector and scalar creation decision require the same exact JSON shape/type and manifest,
  including nullable SAP identity, actor roles/teams, and request evidence, before an identity can
  affect count or offset. SQLite compares JSON structurally and PostgreSQL uses native `jsonb`
  equality; production PostgreSQL key/type predicates are exercised by the declared exact-selector
  acceptance label.

## Loan repayment schedule and ledger reads (010A)

- `GET /api/v1/loan-accounts/{loan_account_id}/repayment-schedule/?page=1&page_size=20`
  and `GET /api/v1/loan-accounts/{loan_account_id}/ledger/?page=1&page_size=20` return the
  standard strict list envelope. They accept only positive `page` and `page_size`, cap page size at
  100, and return `400 VALIDATION_ERROR` for unknown parameters, malformed values, or an
  out-of-range page. An empty collection is page 1 of 1 with `total_count: 0`.
- Both reads reuse the 009J active-user, effective-role, `finance.loan_account.read`, and canonical
  loan-object scope without widening it. Missing authentication returns the shared `401` contract;
  a role without permission or permission without a source role returns `403 FORBIDDEN`; missing,
  cross-scope, and evidence-incoherent account ids share `404 NOT_FOUND`.
- Schedule rows are ordered by `installment_number`, then immutable UUID. Each row contains
  `repayment_schedule_id`, integer `installment_number`, ISO due and nullable extended-due dates,
  decimal-string `principal_due`, `interest_due`, `charges_due`, `total_due`, `paid_principal`,
  `paid_interest`, `paid_charges`, server-derived `amount_received`, bounded `schedule_status`, and
  UTC `created_at`. Stored status is `pending`, `paid`, or `overdue`; S43's partially-paid display
  remains deferred to the allocation owner under A-137. The database requires a positive
  installment number, non-negative amounts,
  `total_due = principal_due + interest_due + charges_due`, and unique
  `(loan_account, installment_number)`. This slice exposes no schedule mutation or generator;
  retained dates and amounts originate in approved term-sheet/loan-agreement ingestion.
- The initial ledger is a deterministic read projection over the singular coherent Epic 009
  successful disbursement owner; it does not copy that owner into a mutable ledger table. The row
  contains ISO `transaction_date`, `transaction_type: disbursement`, typed `owner_reference`, bank
  `reference`, decimal-string debit/credit, principal/interest/total running balances, canonical
  transfer actor id plus display label, the canonical SAP-posting owner's current status, and fixed
  safe remarks. Only `pending` is currently representable under A-135. The opening
  disbursement increases principal and total outstanding, so debit and both running balances equal
  the disbursed amount while credit and interest balance are zero.
- A sanctioned/unfunded account returns an empty ledger. Changed or incomplete transfer/register/
  advice/SAP/audit/workflow evidence cannot create a ledger row. Both endpoints are zero-write and
  introduce no repayment, allocation, interest, DPD, reversal, export, statement, or mutation
  behavior. Later servicing owners extend this projection with append-only/compensating movements;
  posted owner history is never updated or deleted through these interfaces.
- Historical disbursement reconciliation always retains the original funded amount and activation
  date. It deliberately does not freeze later-owned loan status/outstanding balances or the
  SAP-posting owner's lifecycle fields, so legitimate repayment, interest, or future SAP posting
  transitions cannot erase the immutable opening row; relational ids, amounts, action/digest, and
  owner evidence must still agree.

## Staff disbursement workspace (009K)

- `GET /api/v1/disbursement-workspaces/?page=1&page_size=20` returns the standard strict pagination
  envelope. It accepts only positive `page` and `page_size` values, caps page size at 100, and
  rejects out-of-range pages and unknown parameters with `400 VALIDATION_ERROR`.
- The collection requires an active effective Senior Manager Finance role with
  `finance.disbursement.initiate`, current CFC authority with `finance.disbursement.authorise`,
  exact Credit Manager `finance.sap_request.create`, or assigned Senior Finance
  `finance.sap_request.complete`. Role alone, permission alone, intake assignment, or a raw id
  grants no row. Senior Finance initiation rows use the dedicated current-SAP-assignment
  candidate owner; they do not reuse or weaken the public Loan Account read permission. CFC rows
  require the retained CFC-task relation created by the exact initiation owner.
- Each item contains safe account/application/member display facts, Money strings, masked SAP code,
  the canonical current readiness projection when the actor can read it, masked beneficiary/source
  bank display, payment/advice statuses and timestamps, and server-owned `available_actions`.
  Action descriptors carry the exact URL, method, required permission, enabled/disabled reason,
  form fields, and protected fixed identifiers needed by an existing mutation contract. The client
  never derives an action from a status or role label.
- A CFC without readiness-read authority sees only the frozen fact that the accepted initiation
  passed readiness at `initiated_at`; the §31.3 authorisation owner still revalidates current
  initiation/readiness/bank evidence before accepting a decision. This projection cannot authorize
  a payment or substitute for the mutation guard.
- Full account numbers, unmasked SAP/UTR values, encrypted values, checksums, storage/capability
  values, idempotency digests, network context, audit bodies, and provider internals are excluded.
  The collection is transactionally read-only and writes no audit, workflow, task, payment,
  account, register, advice, or borrower truth.
- S36 create/send and S37 completion descriptors come from the SAP module, expose only fixed
  application/member display facts and active permissioned assignee choices, and mark every optional
  completion field optional. Browser `datetime-local` values are serialized as aware ISO-8601 instants.
- §31.4 success also returns `initial_payment_sap_posting` with safe `posting_status` and masked/null
  reference. The singular obligation is atomically tied to transfer/register evidence and begins
  `pending`; no confirmation endpoint exists under A-135.
- 009L5 paginates exact S36 candidates, assigned S37 deliveries, CFC initiation rows, and the combined
  Senior Finance S37/Loan Account sequence at their database identity boundaries. The combined
  order is all current assigned S37 rows followed by eligible Loan Accounts, with offsets applied
  arithmetically across that seam. Their exact owner decisions determine count, offsets, total
  pages, and projected rows without reconciliation overscan. Transfer-success and advice descriptors delegate to their
  mutation owners' current actor/object/evidence predicates instead of role/status inference.
- 009L6 retains an exact selector manifest with each accepted SAP send/completion and disbursement
  initiation audit. S37 selection additionally reconciles the exact communication/task/file/
  workflow actor relations; account completion binds its exact completion body and terminal
  workflow; pending-CFC selection reconciles the exact
  initiation body, readiness JSON, workflow trace, CFC action URL/message, and unfunded aggregate.
  A changed existing key or added/removed key is excluded before count/pagination, so projection
  cannot silently drop an admitted row. Selector manifests are written only with newly accepted
  owner evidence; unverifiable legacy evidence remains ineligible rather than being blessed from
  its mutable current body. No manifest field is exposed in a public response.
- 009L7 makes the send owner complete before count: communication/task identity and cardinality,
  exact action URL, delivery/workflow/audit evidence, Annexure-I file metadata, an immutable
  encrypted-storage checksum snapshot, and verified workbook digest must all agree. Completed
  Loan Account rows consume the same send owner as S37. Pending-CFC selection also applies current
  lifecycle, borrower-bank/cancelled-cheque, and source-bank eligibility before count, so scalar
  reconciliation cannot remove a selected identity or shift a page.

## Direct repayment capture and SAP posting (010B)

`POST /api/v1/loan-accounts/{loan_account_id}/repayments/` requires an active authenticated
`credit_manager` or `accounts_head` with `finance.repayment.create`, source-defined loan scope, and a
nonblank `Idempotency-Key` of at most 255 characters. It accepts exactly direct-farmer source,
positive numeric 18,2 amount, ISO received date, `rtgs`/`neft` method, nonblank bank reference and
remarks, plus an optional statement-line UUID evidence link. The bank reference is NFKC-normalized,
whitespace-collapsed, trimmed, and uppercase for globally unique duplicate comparison.

Success atomically creates one pending-allocation receipt, one safe receipt audit, one urgent Credit
Manager task, and one pending next-working-day SAP obligation. It does not update account balances,
schedule paid amounts, or ledger movements. Exact key/request replay returns
`{idempotency_replayed: true, original_response: <retained result>}` without writes. Changed or
cross-loan key reuse and duplicate canonical bank references return `409 CONFLICT`; validation
returns `400`, missing authority `403`, and inaccessible ids `404`.

`POST /api/v1/repayments/{repayment_id}/mark-sap-posted/` accepts exactly a nonblank bounded
`sap_entry_reference`, timezone-aware `sap_posted_at`, and optional remarks. It requires the same
source role/scope plus `finance.repayment.mark_sap_posted`. The one-way pending-to-posted transition
retains the source SAP reference, actor, timestamp, and safe audit evidence. It records manual SAP
truth without claiming provider integration and never creates a second receipt, obligation,
allocation, or financial movement.

## Principal-first repayment allocation (010C)

`POST /api/v1/repayments/{repayment_id}/allocate/` accepts exactly
`allocation_rule: principal_first`, nonblank remarks of at most 2,000 characters, and a nonblank
`Idempotency-Key` of at most 200 characters. It requires an
active `credit_manager` or `accounts_head`, `finance.repayment.allocate`, and the same source-defined
loan-object scope as repayment capture. Missing authentication returns `401`; malformed input `400`;
missing authority `403`; inaccessible receipt/account ids `404`; ineligible or incoherent retained
receipt/balance evidence returns zero-write `409 CONFLICT`.

The allocator locks the receipt, account, and schedule rows in one transaction. It applies
`min(receipt, principal outstanding)` to principal, then applies only the remaining amount up to
interest outstanding. Charges receive zero until an approved waterfall exists. Any charge-facing or
excess remainder is retained as non-negative `unallocated_amount`, status
`allocated_with_exception`, and reason `charge_or_excess_policy_not_configured`; balances never go
negative. It admits only a coherent terminal SAP posting decision and rejects ordinary allocation of
a `manual_match_exception`. Schedule paid amounts follow A-139, and the exact principal/interest
allocation must fit the locked schedule capacity before any write. Each changed schedule row retains
an immutable per-allocation application record for later reproduction or reversal. Exact payoff
reaches zero and status `repaid`.

Success returns the immutable allocation id/receipt id, `allocation_rule`,
`allocation_rule_version`, allocation status, principal/interest/charge/unallocated decimal strings,
nullable exception reason, and the server-owned post-allocation account balances. It atomically
updates account/schedule truth, appends one immutable repayment ledger row, and writes one safe
allocation audit containing before/after amounts, actor/roles, rule/version, timestamp-owned row, and
request evidence. Exact key/request replay returns the same retained success projection with no
second financial effect. Missing, changed, cross-receipt, or different-key replay returns zero-write
`400`/`409`. Database one-to-one and arithmetic constraints independently prevent duplicate allocations,
duplicate ledger movements, negative balances, unconfigured charge allocation, and inconsistent
before/after totals.

The 010A ledger preserves the canonical disbursement row and appends repayment rows ordered by their
immutable creation identity. A repayment row exposes the allocation owner reference, captured bank
reference, zero debit, only the amount actually allocated as credit, post-allocation running
principal/interest/total balances, retained actor snapshot, current receipt SAP status, and fixed safe
remarks. Unallocated money is observable on the allocation result and is not misrepresented as a
ledger credit.

## Manual allocation approval and financial reversal (010C2)

`POST /api/v1/repayments/{repayment_id}/manual-allocation-approvals/` accepts exactly
`loan_account_id`, positive 18,2 `amount`, and a nonblank `reason` of at most 500 characters, plus a
nonblank `Idempotency-Key` of at most 200 characters. It requires the explicitly assigned critical
`finance.repayment.manual_allocation_approve` permission; no default role receives that permission.
The action succeeds only when the receipt is posted, pending allocation, and linked by 010D's
coherent `bank_statement.line_manually_matched` evidence. Destination, amount, receipt, and statement
line must match exactly. Success returns immutable approval/receipt/account/line ids, approved amount,
terminal `approved` decision, and timestamp. Exact replay returns retained truth; missing, changed,
foreign, drifted, or already-approved attempts are zero-write `400`/`409`.

`POST /api/v1/repayments/{repayment_id}/manual-allocate/` accepts exactly `approval_id`,
`allocation_rule: principal_first`, and nonblank `remarks` of at most 2,000 characters, plus the
allocation `Idempotency-Key`. It requires ordinary source-backed allocation role, permission, and
object scope. The terminal approval must cover the exact receipt, loan, amount, and bank line; then
the action delegates all schedule/account/allocation/ledger math to the canonical 010C allocator.
Response and replay semantics match ordinary allocation.

`POST /api/v1/repayments/{repayment_id}/reverse/` accepts exactly a nonblank `reason` of at most 500
characters and a nonblank `Idempotency-Key` of at most 200 characters. It requires the explicitly
assigned critical `finance.repayment.reverse` permission in addition to ordinary allocation
authority and object scope; no default role receives reversal authority. The server owns the amount
and original source. It accepts only the current unreversed allocation state, restores account and
per-schedule balances from immutable allocation-application evidence, changes the receipt allocation
status to `reversed`, and appends one immutable reversal plus one debit ledger movement. Original
receipt, allocation, schedule-application, and credit-ledger rows are never edited or deleted. Exact
replay returns retained truth; missing, changed, cross-receipt, stale, foreign, and duplicate attempts
fail before financial writes.

Approval, allocation, and reversal evidence retains actor/role, exact linked evidence identities,
before/after money, safe reason hashes, and request/timestamp truth. Free-text reasons, bank
narration, SAP references, and other sensitive bank content are not copied into audit JSON or error
messages; mandatory bounded reasons remain on their immutable governed records.

## Bank statement evidence matching and reconciliation (010D)

`POST /api/v1/bank-statement-imports/` accepts multipart `file` and
`collection_bank_account_id`, plus a
nonblank `Idempotency-Key` of at most 255 characters. Files are restricted UTF-8 CSV, at most
1,000,000 bytes and 500 data lines, with exactly `transaction_date`, `value_date`, `amount`,
`narration`, `reference`, and `loan_account_number` columns. The retained file uses the central
restricted document-storage/provenance seam. `collection_bank_account_id` must be the opaque UUID of
the current active SFPCL account selected by the central source-bank governance seam; raw account
numbers and unverified labels are rejected and the identifier is not echoed. Exact key/body replay
and the same file checksum for the same governed account reuse one import; changed key reuse returns
`409 CONFLICT`.

The importer persists bounded statement facts and safe parse/match reason codes. It automatically
links only one receipt whose normalized bank reference, positive 18,2 amount, received date, and
canonical loan-account number all match exactly. A direct receipt additionally requires an exact
account, application, or borrower narration identity. A subsidiary receipt requires both borrower
name and application reference; either fact alone and account-only narration remain unmatched.
Automatic matching requires `finance.bank_statement.match` and the same loan-object scope as manual
matching. Missing reference/account/narration facts remain unmatched;
invalid row facts and conflicting/already-consumed counterparts remain exceptions. It never creates
a receipt or allocation, updates a financial balance/schedule/ledger, or marks SAP posted. Success
returns import/document ids, safe counts/statuses, and line ids/dates/amount/status/reason facts; it
does not return narration or the raw bank reference.

`GET /api/v1/bank-statement-lines/?match_status=unmatched|matched|exception&page=1&page_size=20`
returns the strict standard list envelope in deterministic creation/id order. Unknown query fields,
invalid statuses, and invalid/out-of-range pagination return `400 VALIDATION_ERROR`. Filtering by
effective loan-object scope happens before counts and pagination, so inaccessible line, receipt, and
aggregate identities are not disclosed.

`POST /api/v1/bank-statement-lines/{line_id}/match/` accepts exactly `repayment_id` and a nonblank
manual `reason` of at most 500 characters. It locks both line and receipt, records the actor/roles,
safe reason code and timestamp in audit evidence, links each side once, and returns a safe nested
receipt-evidence projection. `BankStatementLine.matched_repayment` is the sole database relationship
owner; receipt `bank_statement_line_id` and `statement_match_status` values are derived projections,
never independently writable truth. Manual evidence decisions project `statement_match_status` as
`manual_match_exception` for the later governed reconciliation/allocation owner while leaving
`allocation_status` unchanged. Already-consumed counterparts return `409 CONFLICT`; inaccessible
identities return `404`.

`POST /api/v1/bank-statement-lines/{line_id}/exception/` accepts exactly a nonblank bounded `reason`
and one safe `reason_code`: `evidence_conflict`, `counterpart_not_captured`, or
`requires_investigation`. It records an auditable exception without linking or moving money. A
matched line cannot be changed to an exception, and a retained exception decision cannot be
rewritten under a different code.

Read/import/match require respectively `finance.bank_statement.read`,
`finance.bank_statement.import`, and `finance.bank_statement.match`, plus an active source-authorized
`credit_manager`, `accounts_head`, or `senior_manager_finance` role. Missing authentication returns
`401`; role- or permission-only callers receive `403`. Statement narration, raw references, manual
reasons, and file bytes never enter ordinary API errors, list responses, or reconciliation audits.

## Subsidiary deduction reconciliation (010E)

`GET /api/v1/loan-accounts/{loan_account_id}/repayments/?page=1&page_size=20` is the
010MA staff read projection for S44/S45. It reuses the 010A loan-account read permission, active
source role, object scope, strict pagination validation, and inaccessible-object `404` contract.
Rows are ordered by received date, retained creation time, and immutable repayment id. Each row
contains receipt identity/source, decimal-string amount, received date/method/reference, canonical
statement relationship/status, allocation and SAP statuses/evidence, and nullable retained
allocation parts. Subsidiary rows additionally include company, produce/transfer reference,
tri-party-agreement identity, reconciliation status, and Treasury verification status. This read
never calculates allocation or matching, exposes free-text remarks/narration, or mutates financial
truth.

`POST /api/v1/loan-accounts/{loan_account_id}/repayments/` dispatches
`repayment_source: subsidiary_deduction` to the subsidiary owner. In addition to positive numeric
18,2 amount, ISO received date, nonblank remarks, and a bounded `Idempotency-Key`, it requires
`payment_method: subsidiary_transfer`, a UUID `subsidiary_company_id`, nonblank bounded
`produce_payment_reference`, and matching nonblank `bank_reference_number` and
`transfer_reference`. The transfer reference is NFKC-normalized, whitespace-collapsed, and globally
duplicate-protected; the normalized produce reference is duplicate-protected per subsidiary UUID.
An optional `bank_statement_line_id` is accepted only through 010D's exact claim interface and
therefore also requires its matching authority; malformed, inaccessible, already-decided, or
fact-mismatched lines fail the entire capture transaction. 010D remains the canonical relationship
owner.

Capture requires an active `credit_manager` or `accounts_head`, `finance.repayment.create`, the
existing loan-object scope, a funded serviceable account, and the legal-document owner's current
executed, verified, renderer-valid tri-party agreement. Success atomically retains one pending
receipt, distinct subsidiary/agreement/reference evidence, safe receipt audit, urgent Treasury task,
and pending SAP obligation. It never matches a statement line, verifies Treasury evidence, posts
SAP, allocates money, or changes account/schedule/ledger truth. Exact request/key replay returns the
retained response without writes; missing agreement and duplicate/changed references return
zero-write `409 CONFLICT`.

010D exact matching requires the transfer reference, amount, received date, account number, borrower
name, and application reference. Missing or conflicting narration stays in the existing unmatched
queue with a safe reason. Authorised manual matching remains possible through 010D and is retained
as `manual_match_exception`; neither match path changes balances.

`POST /api/v1/repayments/{repayment_id}/verify-subsidiary-deduction/` accepts exactly nonblank
`remarks` of at most 2,000 characters. It requires `finance.repayment.allocate`, the same active
Credit Manager/Accounts role and object scope, the unchanged captured agreement, and one canonical
010D exact or authorised match. An amount above current total outstanding records
`reconciliation_status: exception` while Treasury status remains pending; it cannot proceed to SAP
or allocation. Success records separate `reconciled` and `treasury_verification_status: verified`
facts with actor, role, statement/agreement identities, timestamp, safe remarks digest, request, and
audit evidence. Exact actor/body replay is zero-write; changed replay is `409 CONFLICT`.

For subsidiary receipts, `POST /api/v1/repayments/{repayment_id}/mark-sap-posted/` additionally
requires coherent reconciliation and Treasury verification. SAP reference, timestamp, and remarks
digest define the exact replay; the same request returns retained truth while a changed terminal
request conflicts. The canonical 010C allocation owner additionally requires the same subsidiary
evidence and canonical statement relationship before it may perform its existing posted-SAP,
principal-first, schedule, account, ledger, audit, and idempotency checks. No subsidiary module code
calculates or writes an allocation or balance directly.

## Effective interest-rate configuration and borrower notices (010E2)

`GET /api/v1/config/interest-rates/?page=1&page_size=20` returns the strict standard list envelope,
ordered by effective date and immutable id. Each row exposes the rate-version id/version, fixed
`floating` rate type, explicit four-decimal effective rate, optional approved benchmark/spread/reset
metadata, inclusive effective dates, communication requirement, Board approval reference, status,
creator/approver ids, activation time, and borrower-notice counts by `pending`, `sent`, and `failed`.
Unknown query fields return `400 VALIDATION_ERROR`. The existing configuration-read permission or
the exact manage permission permits this read; neither grants any unrelated configuration mutation.

`POST /api/v1/config/interest-rates/` accepts exactly `version_number`, `rate_type: floating`,
non-negative four-decimal `effective_rate`, ISO `effective_from`, nullable ISO `effective_to`,
nullable `benchmark_name`, nullable non-negative `spread_rate`, nullable `reset_frequency`, boolean
`communication_required`, and nonblank `board_approval_reference`. It requires
`config.interest_rate.manage` and creates only a `proposed` immutable version plus sanitised audit
evidence. The server never derives the effective rate from optional benchmark/spread values and does
not invent reset or penal-interest policy.

`POST /api/v1/config/interest-rates/{interest_rate_config_id}/activate/` requires the same critical
permission, existing `communications.communication.send` authority, a distinct maker and checker,
and a nonblank `Idempotency-Key` of at most 255 characters.
It locks the complete rate-version set, rejects insertion into approved history, overlaps, and a
successor that does not begin the day after an explicitly closed predecessor. An open predecessor is
closed at the day before its approved successor, so the approved timeline stays contiguous. Exact
replay returns retained activation truth; a changed version/key binding or reactivation returns
zero-write `409 CONFLICT`. Missing authentication returns `401`, missing authority `403`, an unknown
id `404`, and malformed input `400`.

Activation atomically records version/audit evidence and one loan-rate history for each active
floating-rate loan. When communication is required, it creates exactly one loan-level notice
obligation linked to one email and one SMS communication through the existing approved-template
communications dispatcher. The response reports both obligation-level and channel-level status
counts. Queueing remains `pending`; only accepted provider evidence becomes `sent`; exhausted
provider or missing-recipient outcomes remain `failed`. Contact addresses and message bodies never
appear in the rate-activation audit or rate-config response. A failed local fan-out rolls back
activation.

Later annual-invoice and monthly-accrual owners call the configuration module's deterministic
historical resolver with a calculation date. Zero matching active versions fails closed and multiple
matches are treated as corrupt/ambiguous truth. The consumer seam stores an immutable rate id,
version, value, date, loan, and consumer reference; exact replay returns that snapshot, so activating
a later version cannot rewrite an already-consumed calculation.

## Annual interest invoices (010F)

`POST /api/v1/loan-accounts/{loan_account_id}/interest-invoices/` accepts exactly
`financial_year` in `FY2026-27` form and requires a nonblank `Idempotency-Key`. The request does
not accept principal, rate, period, invoice date, tax, fee, paid-interest, or invoice-amount fields.
The canonical interest module locks the scoped serviceable loan, derives the 1 April–31 March period,
principal snapshot, period interest payments, effective approved rate snapshot, and one effective
approved invoice-calculation/owner configuration. Missing or ambiguous benchmark, spread, reset,
day-count, tax, fee, or owner configuration fails closed. Exact replay returns retained truth;
changed replay or another invoice for the same loan/period returns `409 CONFLICT`.

`GET /api/v1/loan-accounts/{loan_account_id}/interest-invoices/` and scoped portfolio
`GET /api/v1/interest-invoices/` return the strict paginated list envelope and accept only optional
`financial_year`, `invoice_status`, `page`, and `page_size`.
Rows expose immutable calculation provenance and recipient-safe delivery status, never borrower
contact details.

`POST /api/v1/interest-invoices/{interest_invoice_id}/issue/` accepts exactly `channel: email`, the
retained borrower `recipient_email`, and nonblank `remarks`, with a nonblank `Idempotency-Key`.
Only the configured owner holding `finance.interest_invoice.issue` and object scope may issue a valid
draft. Issuance stores one PDF, creates one approved-template communication and queued delivery job,
records audit evidence, and transitions only `draft` to `issued`; it never marks an invoice paid.
Exact replay is zero-write and changed terminal replay is `409 CONFLICT`.

## Monthly interest accruals (010G)

`POST /api/v1/loan-accounts/{loan_account_id}/accrual-entries/` accepts exactly
`accrual_month` in `YYYY-MM` form and requires a nonblank `Idempotency-Key`. It rejects caller-
supplied principal, rate, period, method, day count, or accrued amount. The interest module locks the
scoped loan and derives the complete calendar month, canonical month-end principal from immutable
disbursement/repayment-ledger truth, approved effective-rate snapshot as of month end, and the one
effective approved calculation configuration. A repayment posted after the month cannot reduce an
earlier accrual's principal snapshot.
The loan must be funded, serviceable, positive-principal, disbursed by the first day of the month,
and not closed during or before the requested month. Missing/ambiguous calculation or rate truth
returns `409 CONFLICT` with no zero/fabricated accrual.

Success returns immutable loan/month, period, principal/rate/calculation provenance, calculation
days/day-count basis, decimal accrued amount, actor/timestamp, and honest pending SAP status. It
atomically creates one immutable rate-consumption snapshot, accrual audit, accrual row, and pending
SAP posting obligation without changing account balances, repayment allocations, ledgers, or annual
invoice snapshots. The database uniquely constrains `(loan_account, accrual_month)`. Exact key/body
replay returns the retained response with zero writes; changed key reuse or another request for the
same loan/month returns `409 CONFLICT`.

`POST /api/v1/accrual-entries/bulk-generate/` accepts exactly `accrual_month`, required boolean
`dry_run`, and optional `loan_account_ids` containing 1–100 unique UUIDs, plus a nonblank
`Idempotency-Key`. Omitting ids means the caller's bounded all-scoped serviceable-loans set; more
than 100 must be split into selected batches. It requires `finance.accrual.bulk_generate` and applies
the canonical loan scope before calculation. Results remain in requested/canonical order and report each input as
`created`, `existing`, `skipped`, or `failed`, with explicit `persisted`; one inaccessible or invalid
loan does not hide successful loans. Dry run resolves and calculates through the same approved
configuration seams but creates no rate-consumption, audit, accrual, or SAP-obligation rows.

`POST /api/v1/accrual-entries/{accrual_entry_id}/mark-sap-posted/` accepts exactly terminal
`posted_status` (`posted` or `failed`), a nonblank SAP reference only for `posted`, and nonblank
bounded `remarks`, plus a nonblank `Idempotency-Key`. It requires either accrual permission and the
same loan-object scope. The action records actor/time and hashed reference/remarks audit evidence,
updates the retained accrual and its local obligation atomically, and never claims external provider
delivery. Exact replay is zero-write; changed or second terminal evidence returns `409 CONFLICT`.

## Interest capitalisation after 30 April (010H)

`POST /api/v1/interest-capitalisations/check/` accepts exactly `financial_year` in
`FY2026-27` form, an ISO `as_of_date`, and `dry_run: true`. It requires
`finance.interest_capitalise` plus canonical loan-object scope. The check derives each scoped
serviceable loan's eligible issued invoice balance from retained backend truth and returns an
explicit reason, old principal, unpaid interest, and projected new principal. It never consumes an
idempotency key or writes capitalisation, account, ledger, communication, document, or audit truth.

`POST /api/v1/loan-accounts/{loan_account_id}/interest-capitalisations/` accepts exactly
`financial_year` and an ISO `capitalisation_date` strictly after 30 April, plus a nonblank
`Idempotency-Key` of at most 200 characters. It does not accept an unpaid amount, revised principal,
rate/calculation version, recipient, or notification decision from the caller. The interest owner
locks canonical account, invoice, and accrual truth; requires a coherent serviceable account, one or
more issued invoices with positive unpaid interest as of the 30-April cutoff, retained borrower
email, and the approved `interest_capitalisation_notice` template; and derives all monetary values.

Success atomically creates one immutable `(loan account, financial year)` capitalisation and source-
invoice evidence, increases principal and total outstanding by exactly the eligible unpaid interest,
appends one debit ledger movement with post-movement balances, stores rate/calculation/accrual
provenance, queues one official email job, stores one confidential hard-copy PDF artifact, and
records actor/request audit evidence. The response reports the email job's honest queued/retrying/
sent/failed state and the letter document id; queueing never claims provider delivery. Historical
invoice and accrual snapshots remain unchanged, while subsequent principal-as-of calculations and
the ordinary 010A account/ledger reads use the revised principal.

Exact actor/loan/body/key replay returns the retained chain with no second financial effect. Changed
or cross-loan key reuse, another key for the same loan/FY, paid/zero/missing invoices, missing notice
configuration, incoherent account balances, or communication setup failure returns a zero-write
error. Permission or object-scope denial returns `403`; malformed/caller-money input returns `400`;
financial/state conflicts return `409`. A database unique constraint and locked PostgreSQL
transaction ensure concurrent finalisers retain one capitalisation and one ledger movement.

## DPD calculation and monitoring buckets (010I)

`POST /api/v1/loan-accounts/{loan_account_id}/dpd-status/calculate/` accepts exactly an ISO
`as_of_date` and requires `monitoring.dpd.calculate` plus canonical loan-account scope. The loan
must be in an active servicing state. The monitoring owner locks the account, reconstructs each due
schedule line from immutable principal/interest due amounts and allocation/reversal ledger movements
whose transaction date is on or before the requested date, and derives days past due from the
earliest still-unpaid due date. It never accepts caller amounts, dates other than `as_of_date`, or a
caller bucket.

One immutable snapshot is retained per loan/as-of date. It includes principal, interest and total
overdue; calendar-anniversary SOP classification (`current`, `one_to_two_years`,
`two_to_three_years`, `more_than_three_years`); optional separately configured operational
classification (`0_30`, `31_60`, `61_90`, `over_90`); calculation and operational-scheme versions;
source inputs; actor/audit evidence; and creation time. No effective operational scheme yields
`standard_bucket: null`; overlapping effective schemes fail closed. A loan with no unpaid due
schedule is current with zero amounts and no standard bucket. Exact loan/date replay returns the
retained response, creates no second audit/snapshot, and cannot move the account's current pointer
backward from a later as-of snapshot. Calculation never creates reminder, default, extension, or
workflow state.

`GET /api/v1/loan-accounts/{loan_account_id}/dpd-status/` requires the separate
`monitoring.dpd.read` permission and the same account scope, and returns the current (greatest
calculated as-of date) snapshot. Missing authentication returns `401`, missing permission returns
`403`, inaccessible/missing account or snapshot returns `404`, malformed input returns `400`, and
inactive loan or ambiguous operational policy returns `409`.

`GET /api/v1/dpd-statuses/` requires the same read permission and returns the caller's scoped current
DPD rows plus backend-owned SOP bucket counts. Rows add safe loan number, member display name,
account status, canonical outstanding balances, and repayment date for the staff dashboard. Only
the loan's protected current DPD pointer contributes; the browser never reclassifies or aggregates.

`POST /api/v1/dpd-statuses/bulk-calculate/` accepts exactly `as_of_date`, unique
`loan_account_ids` (maximum 100), and boolean `include_all_active_loans`. Callers select either one
or more ids or their bounded scoped active portfolio, never both. It requires
`monitoring.dpd.calculate`, invokes the same per-loan owner, persists one portfolio-run audit, and
returns `run_id`, as-of date, calculated/skipped/failed counts, and one ordered outcome per selected
loan. One invalid/inactive/inaccessible loan does not hide successful loan results. Concurrent
same-loan/date requests serialize on the account and retain one snapshot, one calculation audit, and
one current pointer.

010I2 strengthens that pointer into a protected relationship to the retained snapshot and enforces
at the database write boundary that the snapshot belongs to the same loan. Instance, queryset,
bulk, and direct-SQL writes cannot store dangling or cross-loan identities, and a referenced
snapshot cannot be deleted. The calculation rechecks monitoring permission and canonical loan scope
after locking through the public loan-owned source-decision interface; that immutable decision is
the only schedule/allocation input consumed by monitoring.

Each new response additionally returns `policy_decision` and `calculation_inputs`. The policy
decision freezes `sop_policy_version`, the exact calendar-anniversary/leap-day/inclusivity
convention, and optional operational scheme id/version/effective dates/30-60-90 bounds. Source
inputs freeze ordered schedule lines, paid-as-of amounts, applied allocation identities, and the
as-of date. Reads and replays serialize these retained bytes rather than current scheme fields.
Complete absence of an optional operational scheme retains `standard_bucket: null`; an effective
but non-active scheme or overlapping active schemes returns `409` with no snapshot, audit, or
pointer write. The additive migration freezes these policy facts for coherent legacy snapshots
without recalculating DPD and fails closed on dangling or cross-loan legacy pointers.

## Quarter-end reminder queue (010J)

`POST /api/v1/reminders/quarter-end-runs/` accepts exactly an ISO calendar quarter-end
`quarter_end_date`, `channel` (`sms` or `email`), and `content_template_id`, plus optional exclusive
`continuation_after_loan_account_id` from a preceding truncated response. It requires
`monitoring.reminder.create` plus canonical loan-account scope and processes at most 100 scoped
accounts with an immutable 010I snapshot for that exact quarter end. The DPD owner decides the
one-year boundary by calendar anniversary (including leap-year spans), not by a fixed day count.
The bounded response contains one result per scoped quarter snapshot with `outcome` (`created`,
`retained`, `skipped`, or `failed`), a safe reason, the retained eligibility decision, and an
optional reminder. Aggregate `created_count`, `retained_count`, `skipped_count`, and `failed_count`
must match those rows. Contact/template/late-state failures are isolated per loan, so a later row
cannot conceal an earlier retained reminder or job. It never recalculates DPD or accepts caller
eligibility, recipient, message, status, money, or provider evidence.

The response also returns integer `processed_count`, boolean `truncated`, and nullable
`continuation_after_loan_account_id`. `processed_count` equals the number of disclosed result rows.
When more than 100 eligible scoped identities exist, `truncated` is true and the continuation value
is the last processed loan identity (exclusive: a continuation starts strictly after it); otherwise
`truncated` is false and the continuation value is null.

Each eligible account retains one reminder for `(loan account, quarter end,
outstanding_beyond_one_year, channel)`, including loan/application/member, exact DPD snapshot,
template/rendered-message snapshot, actor, timestamps, audit, and canonical communication link.
`eligibility_decision` retains the first-unpaid date, quarter cutoff, first anniversary,
day-before/on/after position, DPD calculation version, SOP policy version, and boundary convention.
The communications owner validates the approved/effective template and borrower contact, creates
the snapshot, and queues its generic delivery job. The reminder reports `queued`; canonical job
truth supplies later `sent` or `failed` status. Queueing never claims provider acceptance. Exact run
replay returns the retained row with zero new reminder, communication, job, or audit writes.
Concurrent PostgreSQL runs lock the account and the database uniqueness rule retains one complete
identity and delivery chain.

`POST /api/v1/loan-accounts/{loan_account_id}/reminders/` preserves the source §34.3/34.4
interface and adds the required `quarter_end_date`. SMS/email accepts the source reminder type,
channel, `content_template_id`, nonblank bounded `message_body`, and boolean `send_now`; the caller
body cannot override the approved rendered template. Phone accepts reminder type, `phone`, nonblank
bounded message and call outcome, contacted person (`borrower`, `nominee`, or `representative`), an
ISO next-follow-up date on/after quarter end, and `send_now: false`. Phone logs store actor/time and
audit evidence but create no communication or provider row.

`GET /api/v1/loan-accounts/{loan_account_id}/reminders/?page=1&page_size=20` requires `monitoring.dpd.read` and
canonical loan-object scope. It returns retained eligibility, channel, delivery, safe status reason,
call outcome, next follow-up, actor display, and timestamps in the standard paginated envelope. It never returns recipient, contacted
person, rendered message body, template content, or provider-sensitive evidence.

`GET /api/v1/reminders/?page=1&page_size=20` returns the same safe retained projection across every
loan in the caller's canonical object scope, including historical reminders whose loan has no current DPD pointer.

`POST /api/v1/reminders/{reminder_id}/send/` accepts an empty body and required nonblank
`Idempotency-Key`. It rechecks permission, account scope, the DPD owner's current serviceability,
positive outstanding, serviceable account status, current borrower contact, and current effective
template under lock before delegating to the communications job seam. A newer still-overdue DPD
snapshot does not invalidate the retained quarter decision. The same checks run again at worker
execution immediately before the provider adapter; repayment, resolution, revoked scope/contact,
or an ineffective template retains `cancelled`, exhausts the queued job without retry, and invokes
no provider. Exact send replay retains one job. A changed or cross-reminder key returns the binding
`409 CONFLICT` envelope with no second job. Missing authentication is `401`, permission is `403`,
inaccessible objects are `404`, malformed direct-request input is `400`, and invalid state or
changed delivery replay is `409`. Ordinary responses never expose recipient, rendered body, or
provider-sensitive evidence.

## CFO quarterly MIS snapshots (010K)

`POST /api/v1/quarterly-mis-reports/generate/` accepts exactly `financial_year` in
`FY2026-27` form, `quarter` (`Q1`–`Q4`), and the ISO calendar quarter-end `as_of_date`. It requires
one nonblank `Idempotency-Key`, `monitoring.mis.generate`, and the canonical
`finance.loan_account.read` portfolio/account scope. Unknown body keys and a missing key return
`400 VALIDATION_ERROR`; a key already bound to a different payload returns `409 CONFLICT`.
The monitoring owner consumes only loan status history, disbursement/account terms, immutable
repayment/reversal/capitalisation ledgers, the exact 010I DPD snapshot for the cutoff, interest
invoice state, and reminders at or before the cutoff. Missing per-account DPD truth returns
`409 CONFLICT`; the report does not calculate DPD, create reminders, or mutate any source owner.

Success freezes one portfolio snapshot and a versioned report revision containing active-loan,
sanctioned/disbursed, principal/interest/overdue, quarter-repayment, DPD-distribution, over-one-year,
reminder, invoice-status, account-status, and source-id truth. Drill-down rows also retain the loan
application number, borrower display name/type, region, crop, security type, disbursement date,
revised principal when capitalised, last repayment date, and the precise source identities and
calculation versions used. The typed `loan_portfolio_snapshots` summary columns reconcile to the
frozen totals; unavailable typed counts are nullable and paired with explicit availability markers.
Default, grace, extension, non-recoverable, recovery, closure, grievance,
and compliance values owned by later epics are the literal `unavailable`, never fabricated zeroes.
PostgreSQL generation serializes on the FY/quarter/cutoff identity. Exact replay while a draft exists
returns the same report and export identities with zero new snapshot/audit/document writes; after a
submitted/reviewed report, generation creates the next retained revision and never rewrites history.

`GET /api/v1/quarterly-mis-reports/?financial_year=FY2026-27&quarter=Q1&page=1&page_size=20`
returns only reports whose entire frozen portfolio remains in the caller's canonical scope.
`GET /api/v1/quarterly-mis-reports/{id}/` returns the frozen summary, and
`GET /api/v1/quarterly-mis-reports/{id}/drill-down/?page=1&page_size=20` returns its stable retained
rows. Collections require `page >= 1`, `page_size` from 1–100, reject unknown parameters, and use
the standard pagination envelope. Inaccessible report identities return `404` without disclosure.

`POST /api/v1/quarterly-mis-reports/{id}/submit-to-cfo/` accepts exactly one active CFO
`submitted_to_user_id` and one nonblank `Idempotency-Key`, and requires `monitoring.mis.submit` plus
report scope. Only a draft may be
submitted. `POST /api/v1/quarterly-mis-reports/{id}/mark-reviewed/` accepts an empty body, requires
one nonblank `Idempotency-Key` and `monitoring.mis.review`, and is allowed only for that submitted-to
CFO after submission. Exact action replay returns the retained first response with zero writes;
changed payload binding for that action returns `409`. Each
transition locks the report, retains a distinct actor/timestamp/audit row, and rejects invalid or
concurrent order with `409`; reviewed evidence and every portfolio snapshot are immutable.

Generation also stores deterministic internal PDF and XLSX documents from the frozen snapshot.
`GET /api/v1/quarterly-mis-reports/{id}/export/?format=pdf|xlsx` requires `reports.export` plus report
scope and returns retained document metadata, SHA-256 checksum, download descriptor, and the same
frozen totals. Export never reads live account state. Authentication, validation, permission,
nondisclosing not-found, and state failures use the standard `401/400/403/404/409` envelopes.
# Loan Ledger Statement Export (010K2)

The statement interface exports the canonical immutable loan ledger; it does not calculate or store a
second financial truth. The only supported format in this contract is `csv`.

## Request statement

`POST /api/v1/loan-accounts/{loan_account_id}/ledger-statements/`

Requires `finance.loan_account.read`, `reports.export`, object scope, and `Idempotency-Key`. Borrower
portal callers additionally require `portal.loan_account.read_own` and can request only a loan owned by
their active portal member.

```json
{"format":"csv","from_date":"2026-04-01","to_date":"2026-06-30"}
```

The standard success envelope returns `statement_job_id`, `loan_account_id`, `status`, `format`,
`row_count`, `opening_balance`, `closing_balance`, `checksum_sha256`, and `generated_at`. Exact replay
of the same key and payload returns the same job, artifact, and checksum; reuse with another payload is
`400 VALIDATION_ERROR`.

## Statement status and download

- `GET /api/v1/loan-ledger-statements/{statement_job_id}/`
- `GET /api/v1/loan-ledger-statements/{statement_job_id}/download/?capability={signed-token}`

Status is private to the original requester and returns a short-lived relative `download_url` plus
`expires_at`; storage keys and permanent object URLs are never returned. The capability is bound to the
actor, job, loan, document, checksum, and current issue version. A later status request supersedes the
previous capability. Expired, superseded, tampered, cross-user, cross-loan, and guessed-job downloads
return the same nondisclosing `404 NOT_FOUND` shape. Missing export authority returns `403 FORBIDDEN`.

CSV rows retain canonical ordering and include date range, as-of/generated timestamps, opening/closing
balances, owner references, debit/credit and running balances. Transaction references are masked by
default; `reports.export_sensitive` is not implied. Request, generation, accepted download, and denied
download audit events contain job/loan/document/checksum metadata only—never rows, storage keys, raw
bank data, or signed URLs.

## Member portal loan servicing projections (010L)

The following read-only endpoints require an authenticated user with one active `PortalAccount` and
derive member ownership only from that account. A caller-supplied `member_id` is never authority.
Another member's or a guessed loan identity returns nondisclosing `404 NOT_FOUND`; staff, missing,
suspended, or otherwise invalid portal principals cannot read these projections.

- `GET /api/v1/portal/loan-accounts/?page=1&page_size=20`
- `GET /api/v1/portal/loan-accounts/{loan_account_id}/`
- `GET /api/v1/portal/loan-accounts/{loan_account_id}/schedule/?page=1&page_size=20`
- `GET /api/v1/portal/loan-accounts/{loan_account_id}/repayments/?page=1&page_size=20`
- `GET /api/v1/portal/loan-accounts/{loan_account_id}/invoices/?page=1&page_size=20`
- `GET /api/v1/portal/loan-accounts/{loan_account_id}/direct-instructions/`

List/detail exposes only account/application display references, borrower-safe status and closure
state, backend-owned disbursed/outstanding amounts, and the next persisted due line. Schedule exposes
persisted due/paid parts and a server-derived partial display status. Repayment history includes only
SAP-posted, allocated, non-reversed repayment truth with borrower-safe reference, mode, source, and
principal/interest split; pending, unmatched, failed, or reversed receipts are absent rather than
shown as confirmed. Invoice history includes issued invoices only. Collections accept only `page`
and `page_size`, with `page_size` bounded to 1–100, and use the standard list envelope.

Direct instructions are read-only. They expose beneficiary, bank, masked last four, IFSC, required
loan-account narration, backend total due, disabled proof submission, and the source disclaimer only
when one retained, effective `RepaymentInstructionVersion` is active. Missing approval returns
`available: false` and null bank fields. The projection never reuses the unverified
statement-import bank label or the outgoing disbursement source bank as repayment authority.

## Epic 010 terminal servicing owner contracts (CR-015)

`POST /api/v1/loan-accounts/{loan_account_id}/direct-repayment-command/` is the staff UI's sole
composite direct-repayment mutation. It requires the same active `credit_manager`/`accounts_head`,
loan scope, and all three `finance.repayment.create`, `finance.repayment.mark_sap_posted`, and
`finance.repayment.allocate` permissions as the owned substeps. The nonblank `Idempotency-Key`
binds the loan, actor, `capture` object, and `sap_posting` object. The backend transaction owns
capture, retained SAP decision, principal-first allocation, and the complete response; exact replay
returns `{replayed:true,capture,allocation}` from retained truth, while changed payload or account
binding returns `409 CONFLICT` with no additional effect. Validation, permission, and nondisclosing
identity failures use the standard `400/403/404` envelopes.

Concurrent equal-key statement requests converge on one scheduled job, one document, and one
checksum. Borrower CSV uses a reduced schema: date/as-of/generated metadata, opening/closing
balances, masked reference, debit/credit, and running balances. It omits job/account owner ids,
owner-reference JSON, staff identity, SAP status, and internal remarks. An empty borrower statement
contains one metadata row so its period and balances remain explicit.

Portal loan-account, schedule, repayment, and invoice collections retain the standard list envelope.
The frontend follows `pagination.total_pages` and never treats the first page of 100 as the complete
collection. Direct instructions resolve one retained active `RepaymentInstructionVersion`; the
projection includes `projection_version`, `approved_at`, and server-owned `available_actions`, with
bank fields null and actions empty when no effective approved version exists. Runtime/browser
configuration is not repayment authority.

## Global search aggregate (010N)

`POST /api/v1/global-search/`

The initial authenticated request body is
`{ "search": "value", "page_size": 10, "pages": {} }`. A successful response includes a random,
actor-bound `continuation` token retained server-side for five minutes. Subsequent group pages send
`{ "continuation": "opaque-token", "pages": {"members": 2} }` and do not resubmit the raw search
value. Exactly one of `search` or `continuation` is required; invalid, expired, or cross-actor tokens
return the standard nondisclosing `400 VALIDATION_ERROR`.

`page_size` is capped at 20 and `pages` may independently name `members`, `loan_applications`,
`loan_accounts`, `documents`, `repayments`, `compliance_records`, and `audit_logs`. The query is in
the JSON body so sensitive exact values do not enter query-string/access-log or browser-history
surfaces. Unknown fields, wildcard/control characters, non-string values, and values outside 2–120
characters return the standard `400 VALIDATION_ERROR`; an actor may make 30 requests per minute
before the standard `429 RATE_LIMITED` response.

`data.groups` contains only groups for which the actor retains the group's canonical read
permission and object scope. A denied group is absent, including its count. Each included group is
`{items,pagination}` with deterministic ordering, the standard pagination fields, and a hard
100-result cap. Cards share `id`, `result_type`, `title`, visible `identifier`, `status`, optional
`risk_status`/`amount`, `owner`, `last_updated_at`, `last_updated_by`, and server-authorised
`quick_actions`. PAN/Aadhaar/cheque matching uses stored keyed hashes; Aadhaar and bank suffix
matching uses indexed stored last-four fields. Raw sensitive input and identifiers are never
returned or audited. PAN and Aadhaar inputs additionally require their canonical field-specific
sensitive authority; SAP input requires `finance.sap_code.read`; blank-cheque input requires
`security.blank_cheque.manage`; and security summary inputs require security-package or instrument
authority. The registered compliance provider is intentionally empty until 011M3.

As of 011M3, `compliance_records` projects canonical compliance controls, tasks, governed evidence,
money-lending reviews, Section 186 trackers, NBFC principal-business tests, and KYC/re-KYC reviews.
It searches only safe owner fields (control code/name/area, task period, statutory period/state, and
member name/number under KYC object scope); evidence summaries/files, legal opinions, KYC values,
internal notes, snapshot JSON, and restricted identifiers are neither searched nor projected.
Control/task/evidence/KYC object scope reuses their owner/reviewer/member-scope rules; statutory
trackers require their exact read permissions, while Internal Auditor access remains read-only.
Evidence cards expose no file action. Other cards expose `Open` only to the existing compliance
route. A provider exception or malformed card/action mapping omits the whole compliance group,
including its count and error detail, rather than broadening access or fabricating empty success.

## Default case opening and reads (011A)

- `POST /api/v1/loan-accounts/{loan_account_id}/default-cases/open/`
- `GET /api/v1/default-cases/{default_case_id}/`
- `GET /api/v1/default-cases/?default_case_status=&member_id=&loan_account_id=&page=&page_size=`

Open requires `defaults.case.open`, the Credit Manager role, and canonical loan object scope. The
request accepts only `trigger_event=missed_principal_repayment`, `scheduled_due_date`, and an
optional safe `reason`; a caller cannot submit a missed/paid result. The defaults owner locks and
consumes the loan-owned schedule/allocation decision, opens only an unpaid scheduled principal
obligation whose due date has passed, and returns the standard success envelope. The open response
contains the source §35.1 case ID, status, grace dates, and server-derived `available_actions`.
Detail/list additionally expose retained loan, member, schedule, trigger, and safe reason facts.
Exact replay returns the same case; it never appends another audit/workflow transition or changes
servicing balances.

Detail and list require `defaults.case.read` plus defaults-owned object scope. Credit Manager and
Company Secretary use their persisted loan/workflow scope, configured approvers are matched through
the retained required-approver index, and Internal Auditor requires the active audit-read scope
grant. Inaccessible and guessed identities use nondisclosing `404 NOT_FOUND`. List filters are exact,
pagination is stable with `page_size` bounded to 1–100, and all endpoints use the standard envelope.

## Grace tracking and default assessment (011B)

- `POST /api/v1/default-cases/{default_case_id}/assess/`
- The existing default-case detail/list responses add `grace_state`, `current_assessment`, and
  server-authorised `available_actions`.

`grace_state` is derived from the server-local date and canonical loan principal truth: the grace
end date is the final inclusive grace day, a zero canonical principal balance is `cured`, and an
unpaid case is `expired` beginning the next day. A bounded scheduled processor reconciles active
cases, retains cured history, appends workflow/audit evidence, and creates at most one
`default_assessment` scheduler task for an expired case. Its result contains only processed, cured,
expired, task-created, and failure counts; no borrower-sensitive values are logged or returned.

Assessment requires `defaults.assessment.create`, active `credit_assessment` team membership,
`defaults.case.read`, and canonical object scope. The case must be persisted as
`grace_period_expired`, remain unpaid and open, and have no current assessment. The request accepts
only `assessment_type=post_grace`, classification `intentional|non_intentional|unclear`, mandatory
`reason_summary`, one or more same-loan `evidence_document_ids`, optional
`borrower_interaction_summary`, and a mandatory non-empty `recommended_action`. The response stores
and returns the assessment ID, case ID, all retained assessment facts, assessor ID, and server time.
Early, cured, closed, out-of-scope, invalid/missing/foreign-evidence, and duplicate-current attempts
return standard validation, nondisclosing not-found, permission, or conflict envelopes with zero
partial assessment/audit/workflow writes.

## Extension Note workflow (011C)

- `POST /api/v1/default-cases/{default_case_id}/grant-extension/`
- Existing default-case detail/list responses additionally expose `extension_note` and the
  server-authorised `grant_extension` action.

Grant requires `defaults.extension.grant`, the Credit Manager role, `defaults.case.read`, and
canonical default-case scope. The case must remain open and unpaid after inclusive grace expiry,
and its current assessment must be `post_grace`, `non_intentional`, and recommend
`grant_extension`. The request accepts only nonblank `extension_reason`, the day immediately after
grace as `extension_start_date`, the inclusive final day of exactly twelve calendar months as
`extension_end_date`, and a `document_id` identifying a generated `extension_note` LoanDocument in
the exact loan-application file. Callers cannot assert eligibility, payment, loan scope, or approval.

When no extension-specific checker route is configured, a valid grant creates one retained active
note with the Credit Manager as preparer and a null approver; it does not infer an approver from the
sanction matrix. The response returns note/case/loan/document IDs, reason, immutable dates,
preparer/approver IDs, and state. Exact replay returns the same note and transition; changed replay,
a second extension, intentional/unclear or stale assessment, premature/wrong dates, cured/closed
case, foreign/missing/wrong-type document, or insufficient authority returns the standard
validation, permission, nondisclosing not-found, or conflict envelope without partial writes.

The bounded extension-expiry processor reads canonical principal truth. Payment cures the default
without deleting or rewriting the retained note. An unpaid extension becomes `expired` only after
its inclusive end date and creates one retry-safe `default_assessment` review task; it never creates
a Non-Payment Note. Grant, cure, and expiry append audit/workflow evidence, and PostgreSQL locking
plus one-to-one constraints make five concurrent grants/expiry runs converge.

## Recovery action execution (011F)
- `POST /api/v1/recovery-decisions/{recovery_decision_id}/actions/`
- `POST /api/v1/recovery-actions/{recovery_action_id}/complete/`

Company Secretary execution requires the Critical action permission, canonical case scope, the exact approved decision, matching usable security-owner evidence, and governed documents. Initiation retains fair-conduct interaction evidence. Completion atomically posts verified proceeds through the canonical loan-balance owner; exact replay returns the retained action, changed/stale replay conflicts, and SAP remains `pending` without real adapter acceptance.

## Compliance control tracker foundation (011K)

- `GET|POST /api/v1/compliance-controls/`
- `PATCH /api/v1/compliance-controls/{compliance_control_id}/`
- `GET|POST /api/v1/compliance-tasks/`
- `PATCH /api/v1/compliance-tasks/{compliance_task_id}/`
- `POST /api/v1/compliance-tasks/{compliance_task_id}/evidence/`
- `POST /api/v1/compliance-evidence/{compliance_evidence_id}/review/`
- `POST /api/v1/compliance/money-lending-law-reviews/`

Controls require an explicit active owner, distinct reviewer, first due date, valid frequency/type,
evidence requirement, legal basis, missed-risk text, and status. The configured first due date is the
calendar anchor for monthly, quarterly, and annual periods; ongoing controls retain one evergreen
period. Task generation is unique by control/period, rejects changed replay, queues one overdue
escalation, and records the scheduler result. Task completion is owned only by accepted evidence.

Evidence submission requires the assigned owner, submit permission, a confidential/restricted
governed document, and a non-completed matching task. Review requires the configured distinct
reviewer, review permission, a pending submission, and nonblank comments. Rejection remains in
append-only review history and reopens the due/overdue task; accepted evidence, comments, and task
closure are immutable through the public interface. Annual money-lending review is Company
Secretary-only, requires its dedicated permission, matching accepted annual task evidence, and
restricted legal-opinion and Board-note documents. All responses use the standard envelope and
return server-owned `available_actions`.

## Section 186 and NBFC statutory trackers (011L)

- `POST /api/v1/compliance/section-186-trackers/`
- `GET /api/v1/compliance/section-186-trackers/{section_186_tracker_id}/`
- `POST /api/v1/compliance/section-186-trackers/{section_186_tracker_id}/submit-for-review/`
- `POST /api/v1/compliance/section-186-trackers/{section_186_tracker_id}/review/`
- `POST /api/v1/compliance/nbfc-principal-tests/`
- `GET /api/v1/compliance/nbfc-principal-tests/{nbfc_principal_test_id}/`
- `POST /api/v1/compliance/nbfc-principal-tests/{nbfc_principal_test_id}/submit-for-review/`
- `POST /api/v1/compliance/nbfc-principal-tests/{nbfc_principal_test_id}/review/`

Creation requires the exact Critical tracker permission, the matching quarterly 011K task assigned to
the caller, and that task's current accepted governed evidence. Requests add
`compliance_task_id` and `compliance_evidence_id` to the source calculation inputs; NBFC requests
also require the configured `early_warning_threshold_ratio`. The server rejects caller-supplied
derived/review fields, negative inputs, invalid FY/quarter values, zero ratio denominators, foreign
or stale evidence, and maker-checker overlap.

Section 186 stores two Decimal limits, the higher applicable limit, exposure, headroom, equality as
within-limit, and excess as special-resolution-required. NBFC stores four-decimal ratios, triggers
only when both are strictly above 50%, identifies the one-ratio warning case, and applies the frozen
early-warning threshold without changing that statutory trigger. One result per tracker type and
financial-year/quarter is retained. Exact POST replay returns it; changed or duplicate-period replay
returns `409 COMPLIANCE_CONFLICT`.

Reads require the tracker-specific read permission. The preparer must explicitly submit a draft
before the task's snapshotted distinct reviewer may use `compliance.evidence.review` with nonblank
comments, an accepted/rejected decision, and an explicit Board-presentation flag. Accepted
breached/triggered results require Board presentation and a reviewer-owned restricted
`board_document_id`; any declared Board presentation also requires that governed evidence. Review
is final and audited. Calculation inputs/results, evidence,
reviewer identity/role, preparation/review times, Board state, denied access, and exact replay truth
remain server-owned and traceable. All routes use the standard envelope and project only
server-derived `available_actions`.

## KYC / re-KYC compliance tracker (011M)

- `GET /api/v1/kyc-reviews/`
- `GET|PATCH /api/v1/kyc-reviews/{kyc_review_id}/`
- `POST /api/v1/kyc-reviews/{kyc_review_id}/remind/`
- `POST /api/v1/kyc-reviews/{kyc_review_id}/complete/`

The scheduler derives each cycle from the canonical member KYC profile's last completed verification,
calculates the due date two calendar years later (29 February clamps to 28 February), and begins
tracking at the governed 30-day warning boundary. One member/cycle review, one linked `KYC_AML`
compliance task, one due reminder identity, one overdue reminder identity, and one date-keyed
scheduled-job outcome are retained. Exact replay is zero-duplicate; changed task/review facts conflict.

List filters are `status`, `due_within_days=30`, `member_type`, `member_status`,
`assigned_to_me`, `page`, and `page_size`. A manager requires
`compliance.kyc_review.manage` plus member object scope. Compliance/CFO readers with
`compliance.task.read` see only assigned/reviewer rows; a governed Internal Auditor with an active
persisted `audit_readonly` grant receives safe read-only summaries. List payloads contain no KYC
document identifiers or PAN/Aadhaar values.

`PATCH` accepts exactly `assigned_to_user_id`. Only the current assigned owner may select a distinct,
active user who also has the manage permission and member scope. `remind` accepts an empty body and
requires `Idempotency-Key`; it queues the applicable approved `kyc_rekyc_request_email` or
`kyc_rekyc_request_sms` template through the communications dispatcher and reports only `queued`,
`sent`, or `failed` from retained job truth.

`complete` accepts an empty body. It cannot update KYC facts. Completion requires a strictly newer
profile verification, the same governed verifier on at least one verified KYC document record, and a
currently complete projection: encrypted/verified PAN, verified Aadhaar and photo, CKYC consent,
verified FPC/producer-institution beneficial ownership when applicable, no unverified retained
nominee, and a governed risk rating. It atomically records before/after state, verifier, completion
time, restricted evidence identifiers, closes the linked task, and audits safe identifiers only.
Caller-supplied status, stale/same-cycle evidence, incomplete KYC, foreign scope, reviewer overlap,
invalid filters, changed replay, and direct retained-review mutation are rejected.

## Member portal KYC correction requests (011M2)

- `GET|POST /api/v1/portal/kyc-corrections/`
- `POST /api/v1/portal/kyc-corrections/evidence/`
- `GET /api/v1/kyc-correction-requests/`
- `POST /api/v1/kyc-correction-requests/{kyc_correction_request_id}/review/`
- `POST /api/v1/kyc-correction-requests/{kyc_correction_request_id}/approve/`
- `POST /api/v1/kyc-correction-requests/{kyc_correction_request_id}/reject/`

Portal scope comes only from the authenticated active `PortalAccount`. Evidence upload accepts one
PDF/JPG/PNG KYC file, requires self-attestation for PAN/Aadhaar, stores it as restricted, and retains
portal-account/member provenance. Submission accepts `changes` containing PAN, Aadhaar, mobile
number, email, and/or registered address, a nonblank reason, and at least one document uploaded by
that same portal user for that member.
Caller-supplied `member_id` is never authority; a foreign claim is denied and audited.

Submission creates a pending governed identity-change request but does not mutate member or KYC
state. Portal responses contain masked requested values, borrower-safe status
(`submitted`, `under_review`, `approved`, `rejected`), evidence metadata, dates, and the rejection
reason. They never contain the reviewer identity, internal notes, storage keys, or full identity
values.

The staff queue requires `members.member.update` and canonical member object scope. Review assigns
the acting reviewer, retains internal notes, and registers the restricted evidence in the 004H KYC
document workflow. Approval requires every linked KYC document to be governed-verified; protected
identity fields additionally require `members.member.identity_change.approve` and use the existing
identity-governance path. Approved contact/address changes use the governed member update path.
Both write history, reset KYC to pending reverification, and link an open 011M KYC review when one
exists. Rejection requires a borrower-visible reason and writes no member history. Submit, review,
approve/apply, reject, and cross-scope denial are audited; every lifecycle transition writes the
canonical workflow event.

## Grievance workflow (011N)

- `GET|POST /api/v1/grievances/`
- `GET|PATCH /api/v1/grievances/{grievance_id}/`
- `POST /api/v1/grievances/{grievance_id}/resolve/`
- `GET /api/v1/grievances/{grievance_id}/documents/{document_id}/download/`

Create and resolve require `Idempotency-Key`. Create accepts the source §38 fields plus optional
matching `default_case_id`, `recovery_action_id`, and unique `supporting_document_ids`; caller-named
loan/application/default/recovery records must all belong to the named member and one coherent
source chain. The caller supplies the explicit configured owner and due date because no universal
TAT is source-defined. The server generates one `GRV-{year}-{identity}` reference and derives
`tat_days`, `days_overdue`, and `is_overdue` from retained server dates.

List filters are `status`, `member_id`, `grievance_category`, `assigned_to_user_id`, `overdue`,
`page`, and `page_size`. Staff reads require `compliance.grievance.read` plus canonical member
scope; Internal Auditor is portfolio read-only only while its persisted `audit_readonly` grant is
active. `PATCH` lets Company Secretary reassign to an active,
member-scoped grievance reader and lets only the assigned owner advance `open` to `investigating`
with internal notes. Escalation and resolution use their dedicated module interfaces.

Resolve accepts a required nonblank `resolution_summary`, optional governed
`resolution_document_id`, and optional borrower acknowledgement. It is terminal, retry-safe, and
queues the approved effective `grievance_resolution_email` or `grievance_resolution_sms` template
through the communications dispatcher. `borrower_informed` becomes true only from retained sent
communication evidence; queued delivery never claims success. The 011K job calls the same grievance
owner to escalate overdue and recovery-conduct cases exactly once without resolving them.

The borrower primitive derives member scope from an active portal account, rejects caller-supplied
member identity, and exposes only safe status/resolution/notice truth. Internal notes, recovery
notes, assignee facts, document identities, and staff history remain excluded. Creation, assignment,
investigation, escalation, resolution, notice queue, governed download, and every denied
cross-object attempt are audited.

## Member portal communications, grievances, notifications, and closure (011NA)

- `GET /api/v1/portal/notices/`
- `GET /api/v1/portal/notices/{communication_id}/download/`
- `GET|POST /api/v1/portal/grievances/`
- `GET /api/v1/portal/grievances/{grievance_id}/`
- `GET /api/v1/portal/notifications/`
- `POST /api/v1/portal/notifications/{notification_id}/mark-read/`
- `GET /api/v1/portal/closures/`

Every route derives the member from an active portal account and rejects caller-supplied member
identity. Notice and notification lists include only direct member/user recipients; role and team
notifications are intentionally excluded from the member portal. Notice downloads are available
only when the member-owned communication is backed by an issued NOC or interest-invoice document,
and return the existing short-lived audited document descriptor rather than raw storage paths.

Portal grievance creation accepts `grievance_category`, required `subject`, required `description`,
and optional matching `loan_account_id`/`loan_application_id`, plus `Idempotency-Key`. The portal
never accepts an owner, due date, or member id. The backend uses the explicitly configured
`SFPCL_PORTAL_GRIEVANCE_OWNER_ROLE_CODE` and positive integer
`SFPCL_PORTAL_GRIEVANCE_TAT_DAYS`; missing configuration or a missing active member-scoped owner
returns `409 CONFIGURATION_REQUIRED`. Borrower projections expose the reference, category,
subject/description, source loan/application ids, received/due dates, status, overdue truth,
resolution summary, closure time, informed state, and acknowledgement state only.

Notification mark-read requires the current `read_state_version`; stale writes return
`409 STALE_WRITE`, and foreign identifiers are nondisclosing. Closure rows project only the
authenticated member's loan number, repayment/closure/NOC state, security-return items, and CDSL
unpledge state. An absent CDSL return record remains `pending`; `not_applicable` is shown only when
retained security-return evidence says so.

## Internal Auditor Epic 011 read view (011O)

- `GET /api/v1/auditor/epic-011/`
- `GET|POST /api/v1/compliance/section-186-trackers/`
- `GET|POST /api/v1/compliance/nbfc-principal-tests/`

The focused aggregate requires the active `internal_auditor` role,
`reports.compliance.read`, and that exact role's active persisted `audit_readonly` grant. It returns
four bounded read families: nested default/assessment/extension/non-payment/recovery truth,
closure/NOC/security-return/archive summary truth, controls/tasks/evidence/statutory/KYC/
money-lending truth, and grievances. Every row carries immutable audit/workflow identifiers when
recorded. Evidence is metadata only (`evidence_id`, governed document id/name, sensitivity, source,
period, review state, and the existing guarded download path); file content remains behind the
document owner's permission, object-scope, reason, audit, and signed-download contract.

The projection recursively omits `available_actions`. It does not grant evidence review, audit
observation, export, or any operational permission. The auditor permission catalogue therefore
contains only reads for these families. All Epic 011 POST/PATCH operational calls reject an auditor
with `403` before payload validation or object lookup, and denied calls create no domain write.
Inactive/missing audit scope also denies the aggregate and the underlying compliance control, task,
evidence, statutory, KYC, money-lending, and grievance query owners. Normal staff/member object
filters are unchanged.

The Section 186 and NBFC collection routes now expose GET list projections in addition to their
existing POST calculation contracts. GET accepts optional `search`, returns the standard bounded
list envelope, and uses the same tracker serializers; an auditor receives action-free output because
it has no create/review authority.

## Read-only report APIs (012A)

The six foundation section-40 report routes are `GET` only and return the standard top-level list envelope with
`page` (default 1), `page_size` (default 20, maximum 100), stable ordering, and no write/audit side
effect:

- `/api/v1/reports/application-pipeline/` accepts inclusive `from_date`/`to_date`, `status`, and
  `stage`. Rows are the canonical Loan Request Register entries and retain their application,
  member, reference, amount, stage, and lifecycle-status identifiers.
- `/api/v1/reports/documentation-readiness/` accepts checklist `status`; contracted `pending`
  includes every not-yet-ready checklist, while canonical checklist status values remain accepted.
  Rows are canonical post-sanction checklists with required/completed/pending counts and pending
  item codes.
- `/api/v1/reports/disbursement-pending/` has no report-specific filters. Rows are persisted
  disbursements whose authorisation is pending/approved and whose bank transfer is
  pending/processing.
- `/api/v1/reports/loan-portfolio/` accepts `as_of_date` (default server-local current date) and
  loan-account `status`. The cutoff includes accounts created on or before that date; row amounts
  and statuses are the persisted loan-account projection and are not recalculated by the report.
- `/api/v1/reports/dpd/` accepts `as_of_date` (default server-local current date) and
  `sop_bucket`. It returns the latest persisted DPD snapshot on or before the cutoff for each
  scoped account.
- `/api/v1/reports/compliance-dashboard/` accepts `financial_year=FYyyyy-yy` and returns the
  persisted Section 186 and NBFC principal-business tracker rows for that year.

Malformed dates, reversed ranges, unsupported controlled values, unknown parameters, invalid page
values, and `page_size > 100` return `400 VALIDATION_ERROR`. Unauthenticated access returns 401.
Missing report/owner permission or persisted object scope returns 403 without `data` or
`pagination`, so denied totals are never disclosed. Documentation readiness uses
`documents.checklist.read`; disbursement pending uses `finance.disbursement.readiness`; the other
four routes use their existing `reports.*.read` code plus the canonical owning-domain read scope.
No caller-supplied role or team changes result scope.

## Finance and servicing report catalogue (012A2)

The report registry additionally exposes these stable `GET` routes. Every route returns the
standard bounded list envelope, rejects unknown parameters, uses deterministic owner ordering, and
never mutates or recalculates owning-domain truth:

| Code / route | Filters | Source fields and totals | Permission and owner scope |
|---|---|---|---|
| `credit-sanction` | `financial_year`, `decision` | Canonical Credit Sanction Register projection; `pagination.totals.sanctioned_amount` across the complete filtered scope | `approvals.sanction_register.read` plus canonical approval-case read scope |
| `exception` | `status`, `exception_type` | Canonical Exception Register projection | `approvals.exception_register.read` plus canonical approval-case read scope |
| `security-custody` | `instrument_type=sh4\|blank_dated_cheque` | Governed public custody identity, package/application/account/member ids, status, location, and retained update time; custody evidence and actor ids are omitted | `security.package.read` plus the security evidence coordinator's Stage-4/object scope |
| `sap-pending` | `request_status=draft\|sent` | Exact assigned Finance workspace projection; SAP/customer and identity values remain masked/minimised | `finance.sap_code.read`; the canonical assigned-workspace selector additionally requires the exact active Senior Manager Finance completion scope |
| `disbursement` | inclusive `from_date`/`to_date`, `authorisation_status`, `bank_transfer_status` | Full persisted amount, payment method, authorisation/transfer status, UTR/reference, initiation/authorisation/disbursement dates; `pagination.totals.disbursement_amount` | `finance.disbursement.readiness` plus canonical loan-account scope |
| `repayment` | inclusive `from_date`/`to_date`, `repayment_source`, `allocation_status`, `sap_posting_status` | Persisted receipt amount/date/method/reference and allocation/SAP status; `pagination.totals.amount_received` | `finance.loan_account.read` plus canonical loan-account scope |
| `interest-invoice` | `financial_year`, `invoice_status` | Canonical Interest Invoice owner projection | `finance.loan_account.read` plus canonical loan-account scope |
| `interest-accrual` | `accrual_month=YYYY-MM`, `sap_posting_status` | Canonical accrual snapshot projection; `pagination.totals.interest_accrued_amount` | `finance.loan_account.read` plus canonical loan-account scope |
| `cfo-quarterly-mis` | required `financial_year`, `quarter=Q1\|Q2\|Q3\|Q4` | Canonical frozen Quarterly MIS projection including its source-owned totals and availability map | `finance.loan_account.read` plus the MIS owner's complete frozen portfolio scope |

All routes also accept `page` and `page_size` (default 1/20, maximum 100). Controlled status values
come from the owning persisted model vocabulary. Monetary totals use the same filtered, object-scoped
query before pagination and are formatted as two-decimal strings. Empty authorised results return
`data: []`, zero monetary totals where applicable, and the standard empty pagination projection.
Missing permission or object scope returns `403` without row or total disclosure. Export generation
and unmasked sensitive values are not part of these reads.

## Default, compliance, and audit report catalogue (012A3)

The final catalogue routes use the same bounded list envelope, stable ordering, fail-closed
unknown-filter handling, and source-owner scope as the 012A/012A2 routes:

| Code / route | Filters | Source fields and totals | Permission and owner reconciliation |
|---|---|---|---|
| `default` | `default_case_status`, `member_id`, `loan_account_id` | Exact canonical Default Case list projection and pagination; recovery evidence remains owner-permission projected | `defaults.case.read` plus the Default workflow's role, approval-attribution, and audit-read scope |
| `recovery` | `decision`, `action_status` | Decision/case/account/member identity, action status/type and recovered amount; `pagination.totals.amount_recovered`; approval evidence, security evidence, document ids, reasons, and interaction logs are omitted | `defaults.case.read` plus the Default workflow's canonical case scope |
| `closure-noc` | inclusive `from_date`/`to_date`, `closure_stage=financially_closed` | Closure/account/member identity, NOC issue/delivery status, security-return status, archive identity and retention date; document and archive locations are omitted | `closure.readiness.read` plus the Closure owner's Credit Manager, Company Secretary, or active audit-read scope |
| `section-186` | `financial_year`, `quarter`, `review_status` | Canonical statutory tracker projection without action or Board-document authority; complete filtered applicable-limit and exposure totals | `compliance.section186.read` plus active auditor scope where applicable |
| `nbfc-test` | `financial_year`, `quarter`, `review_status` | Canonical principal-business-test ratios, trigger/warning truth, and review state without action or Board-document authority | `compliance.nbfc_test.read` plus active auditor scope where applicable |
| `kyc-rekyc` | owner filters `status`, `due_within_days=30`, `member_type`, `member_status`, `assigned_to_me` | Canonical scoped KYC review summary with status-only PAN/Aadhaar/consent facts; no identifiers, encrypted values, documents, or actions | `compliance.kyc_review.manage` with member scope, or the KYC owner's governed `compliance.task.read` role/scope |
| `stamp-duty` | inclusive `from_date`/`to_date`, `status`, `stamp_type` | Legal-owner stamp identity/type/amount/status/dates and notarisation status; evidence files and remarks are omitted | `documents.checklist.read` plus the canonical sanctioned-documentation application scope |
| `money-lending-review` | `financial_year`, `state`, `applicability` | Annual review identity, period/state/applicability, task/evidence metadata and reviewer/time; legal-opinion/Board document ids and remarks are omitted | `compliance.money_lending_review.manage` or scoped `compliance.task.read`, including active auditor scope |
| `grievance` | owner filters `status`, `member_id`, `grievance_category`, `assigned_to_user_id`, `overdue` | Canonical scoped grievance identity, linkage, dates, category, state, TAT/overdue and resolution status; descriptions, internal notes, documents, history, and actions are omitted | `compliance.grievance.read` plus the Grievance owner's member scope |

All routes also accept `page` and `page_size` (default 1/20, maximum 100). Invalid controlled
values, malformed dates/UUIDs/financial years, reversed ranges, unknown parameters, and
unauthorised object scope fail closed. Empty authorised results return the standard empty page;
denied results disclose neither rows nor totals. Default-masked report rows never grant reveal or
document-download authority.

`audit-log-export` is registered only as the restricted handoff
`012C-sensitive-export-policy+012D-audit-selector`. Its registry definition has no selector, and
`GET /api/v1/reports/audit-log-export/` always returns `403` even when the caller holds
`audit.audit_log.read`, `audit.export`, `reports.export`, and `reports.export_sensitive`. It cannot
query audit rows or create/download a file through the generic report route. The later export flow
must require the canonical restricted audit read, `audit.export`, general/sensitive export policy
as applicable, a reason, sanitised 012D values, expiring download authority, and audited request
and download events; it must not copy report rows or sensitive filters into audit payloads.
